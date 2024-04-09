import os
import json
from django.core import serializers
from .models import Vehicle, Scan, CompletedScan
from .s3_utils import get_object, generate_presigned_url_get, generate_presigned_url_put
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.utils import timezone
import threading
from .forms import ScanForm, VehicleForm, VisualizationForm
from .perform_scan import complete_scan
from .plot_visualizations import viz_overhead


def index(request):
    return render(request, 'lidar/index.html', {})


def add_vehicle(request):
    return render(request, 'lidar/add-vehicle.html', {})


def data_upload(request):
    if request.method == 'POST':
        print("request was a POST")
        vehicle_form = VehicleForm(request.POST, request.FILES)
        scan_form = ScanForm(request.POST, request.FILES)
        print(f'scan form errors: {scan_form.errors}')
        print(f'vehicle form errors: {vehicle_form.errors}')
        if scan_form.is_valid() and vehicle_form.is_valid():
            print("Both forms valid")
            vehicle = vehicle_form.save(commit=False)
            print("vehicle form saved to a Vehicle object")
            obj, created = Vehicle.objects.update_or_create(
                vehicle_make=vehicle.vehicle_make,
                vehicle_model=vehicle.vehicle_model,
                vehicle_year=vehicle.vehicle_year,
                defaults={"vehicle_updated": timezone.now()},
                create_defaults={"vehicle_make": vehicle.vehicle_make,
                                 "vehicle_model": vehicle.vehicle_model,
                                 "vehicle_year": vehicle.vehicle_year,
                                 "vehicle_body_class": vehicle.vehicle_body_class,
                                 "vehicle_weight_class": vehicle.vehicle_weight_class}
            )
            print("vehicle query successful")
            scan = scan_form.save(commit=False)
            if created:
                print("vehicle not found: assigning new vehicle to scan")
                scan.vehicle = obj
                print(
                    f"new vehicle, {obj.vehicle_make} {obj.vehicle_model} {obj.vehicle_year}, saved")
            else:
                print("vehicle found: assigning old vehicle to scan")
                vehicle = Vehicle.objects.get(
                    vehicle_make=vehicle.vehicle_make, vehicle_model=vehicle.vehicle_model, vehicle_year=vehicle.vehicle_year)
                scan.vehicle = vehicle
                print(
                    f"previous vehicle, {vehicle.vehicle_make} {vehicle.vehicle_model} {vehicle.vehicle_year}, updated")
            scan.save()
            print("scan form saved")
            return HttpResponseRedirect(f'/windshield_removal/{scan.id}')
            # return render(request, 'lidar/windshield-removal.html', {'scan_id': scan.id})

    else:
        vehicle_form = VehicleForm()
        scan_form = ScanForm()
    return render(request, 'lidar/data-upload.html', {'scan_form': scan_form, 'vehicle_form': vehicle_form})


def faq(request):
    return render(request, 'lidar/faq.html', {})


def instructions(request):
    return render(request, 'lidar/instructions.html', {})


def vehicle_database_loading(request):
    return render(request, 'lidar/vehicle-database-loading.html', {})


def vehicle_database_table(request):
    vehicle_list = Vehicle.objects.all()
    for vehicle in vehicle_list:
        vehicle.vehicle_updated = vehicle.vehicle_updated.date()
    completed_scan_list = CompletedScan.objects.all()

    vehicle_list = json.loads(serializers.serialize("json", vehicle_list))
    completed_scan_list = json.loads(
        serializers.serialize("json", completed_scan_list))
    for completed_scan in completed_scan_list:
        completed_scan["vehicle"] = json.loads(serializers.serialize(
            "json", [Scan.objects.get(pk=completed_scan["fields"]["raw_scan"])]))[0]["fields"]["vehicle"]

    return render(request, 'lidar/vehicle-database-table.html',
                  {'vehicle_list': vehicle_list, 'completed_scan_list': completed_scan_list})


def visualization(request, scan_id):
    scan = Scan.objects.get(pk=scan_id)
    vehicle = scan.vehicle
    make = vehicle.vehicle_make
    model = vehicle.vehicle_model
    year = vehicle.vehicle_year
    viz_form = VisualizationForm()
    print(f"Scan status on load: {scan.scan_status}")
    if scan.scan_status == "modifying":
        scan.scan_status = "modified"
        scan.save()

    if scan.scan_status == "modified":
        print("Tried to load Visualization page. Scan about to be processed.")
        thread = threading.Thread(
            target=complete_scan, args=(scan, vehicle))
        thread.start()
        return render(request, 'lidar/visualization.html', {'VisualizationForm': viz_form, 'scan_id': scan_id, 'make': make, 'model': model, 'year': year, 'date': scan.scan_added, 'graph': None, 'graph_str': None, "loading": True})

    if scan.scan_status == "calculating":
        print("Tried to load Visualization page. Scan is still being processed.")
        return render(request, 'lidar/visualization.html', {'VisualizationForm': viz_form, 'scan_id': scan_id, 'make': make, 'model': model, 'year': year, 'date': scan.scan_added, 'graph': None, 'graph_str': None, "loading": True})

    if scan.scan_status == "processed":  # scan should be processed and status updated as such
        num_completed_scans = CompletedScan.objects.filter(
            raw_scan=scan).count()

        if num_completed_scans > 0:
            if request.method == 'POST':
                print("visualization form submitted, request was POST")
                viz_form = VisualizationForm(request.POST)
                if viz_form.is_valid():
                    print("viz_from was valid")
                    completed_scan = CompletedScan.objects.get(raw_scan=scan)

                    eye_pos = int(
                        viz_form.cleaned_data['eye_position_selected'])
                    vrus_selected = list(
                        map(int, viz_form.cleaned_data['vru_selected']))

                    print("Loading Visualization page. Scan is processed.")

                    vehicle_str = f"{year} {make} {model}"
                    [graph, graph_str] = viz_overhead(
                        json.loads(completed_scan.nvp_xs), json.loads(completed_scan.nvp_ys), (scan.F_m + ((scan.E_m - scan.F_m) / 2)), ((scan.B_m - scan.A_m) / 2), eye_pos, vrus_selected, vehicle_str)
                    return render(request, 'lidar/visualization.html', {'VisualizationForm': viz_form, 'scan_id': scan_id, 'make': make, 'model': model, 'year': year, 'date': scan.scan_added, 'graph': graph, 'graph_str1': graph_str[0], 'graph_str2': graph_str[1], "loading": False})

            return render(request, 'lidar/visualization.html', {'VisualizationForm': viz_form, 'scan_id': scan_id, 'make': make, 'model': model, 'year': year, 'date': scan.scan_added, 'graph': None, 'graph_str1': None, 'graph_str2': None,  "loading": False})

        print("Tried to load Visualization page. Scan should be processed, some error occurred.")
        return render(request, 'lidar/404.html', {})


def windshield_removal(request, scan_id):
    scan = Scan.objects.get(pk=scan_id)
    scan_file = scan.lidar_scan
    print(f"scan_status upon windshield: {scan.scan_status}")
    post_windshield_strings = {"modified", "calculating", "processed"}
    if scan.scan_status == "uploaded":
        scan.scan_status = "modifying"
        scan.save()
    elif (scan.scan_status in post_windshield_strings):
        # if clean scan already submitted, do not allow user to go back to page
        print(
            "Scan already modified and cleaned, cannot go back to windshield_removal page.")
        return render(request, 'lidar/404.html', {})

    # print(f'Got scan_file: {scan_file}, {type(scan_file)}')
    scan_path = scan_file.name
    print(f'{scan_path = }')
    obj = get_object(scan_path)
    # print(obj)
    get_url = generate_presigned_url_get(scan_path)
    put_url = generate_presigned_url_put(scan_path)
    # print(f'{get_url = }')
    # print(f'{put_url = }')
    return render(request, 'lidar/windshield-removal.html',
                  {'scan_id': scan_id, 'scan_path': scan_path, 'get_url': get_url, 'put_url': put_url})
