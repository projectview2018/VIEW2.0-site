from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.utils import timezone
import threading
from .forms import ScanForm, VehicleForm
from .perform_scan import complete_scan, access_object
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
            thread = threading.Thread(
                target=complete_scan, args=(scan, vehicle))
            thread.start()
            # return HttpResponseRedirect('/windshield_removal')
            return render(request, 'lidar/windshield-removal.html', {})
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


def visualization(request, vehicle_id):
    vehicle = Vehicle.objects.get(pk=vehicle_id)
    make = vehicle.vehicle_make
    model = vehicle.vehicle_model
    year = vehicle.vehicle_year
    return render(request, 'lidar/visualization.html', {'make': make, 'model': model, 'year': year})


def windshield_removal(request):
    return render(request, 'lidar/windshield-removal.html', {})
