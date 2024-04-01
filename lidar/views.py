from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.utils import timezone
import threading
from .forms import ScanForm, VehicleForm
from .perform_scan import complete_scan
from .s3_utils import get_object, generate_presigned_url_get, generate_presigned_url_put
from .models import Vehicle, Scan, CompletedScan
from django.core import serializers
import json
import os


def index(request):
    return render(request, 'lidar/index.html', {})


def add_vehicle(request):
    return render(request, 'lidar/add-vehicle.html', {})

# handle data upload old


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

    vehicle_list = json.loads(serializers.serialize("json", vehicle_list))

    return render(request, 'lidar/vehicle-database-table.html',
                  {'vehicle_list': vehicle_list})


# def visualization(request, vehicle_id):
#     vehicle = Vehicle.objects.get(pk=vehicle_id)
#     make = vehicle.vehicle_make
#     model = vehicle.vehicle_model
#     year = vehicle.vehicle_year
#     return render(request, 'lidar/visualization.html', {'make': make, 'model': model, 'year': year})

def visualization(request, vehicle_id):
    scan = Scan.objects.get(pk=vehicle_id)
    vehicle = scan.vehicle
    make = vehicle.vehicle_make
    model = vehicle.vehicle_model
    year = vehicle.vehicle_year
    print(f"Scan status on load: {scan.scan_status}")
    if scan.scan_status == "modifying":
        scan.scan_status = "modified"
        scan.save()

    if scan.scan_status == "modified":
        print("Tried to load Visualization page. Scan about to be processed.")
        thread = threading.Thread(
            target=complete_scan, args=(scan, vehicle))
        thread.start()
        return render(request, 'lidar/404.html', {})
    elif scan.scan_status == "calculating":
        print("Tried to load Visualization page. Scan is still being processed.")
        return render(request, 'lidar/404.html', {})
    elif scan.scan_status == "processed":  # scan should be processed and status updated as such
        num_completed_scans = CompletedScan.objects.filter(
            raw_scan=scan).count()
        if num_completed_scans > 0:

            completed_scans = CompletedScan.objects.filter(raw_scan=scan)
            completed_scan = completed_scans.latest("completed_scan_added")
            print("Loading Visualization page. Scan is processed.")
            return render(request, 'lidar/visualization.html', {'make': make, 'model': model, 'year': year})
        else:
            print(
                "Tried to load Visualization page. Scan should be processed, some error occurred.")
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
