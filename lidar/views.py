from django.shortcuts import render
from django.http import HttpResponseRedirect
import threading
from .forms import ScanForm, VehicleForm
from .perform_scan import complete_scan
from .models import Vehicle
from django.core import serializers
import json


def index(request):
    return render(request, 'lidar/index.html', {})


def add_vehicle(request):
    return render(request, 'lidar/add-vehicle.html', {})

# handle data upload old


def data_upload(request):
    if request.method == 'POST':
        vehicle_form = VehicleForm(request.POST, request.FILES)
        scan_form = ScanForm(request.POST, request.FILES)
        if scan_form.is_valid():
            scan = scan_form.save()
            vehicle = Vehicle.objects.get(pk=scan.vehicle.id)
            thread = threading.Thread(
                target=complete_scan, args=(scan, vehicle))
            thread.start()
            return HttpResponseRedirect('/visualization', {"scan_path": scan.lidar_scan})
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
    # if request.method == 'POST':
    #     visual_form = VisualForm(request.POST, request.FILES)
    #     if visual_form.is_valid():
    #         return HttpResponseRedirect('/visualization', vehicle_id)
    # else:
    vehicle_list = Vehicle.objects.all()
    for vehicle in vehicle_list:
        vehicle.vehicle_updated = vehicle.vehicle_updated.date()

    vehicle_list = json.loads(serializers.serialize("json", vehicle_list))

    return render(request, 'lidar/vehicle-database-table.html',
                  {'vehicle_list': vehicle_list})


def visualization(request, vehicle_id=None):
    return render(request, 'lidar/visualization.html', {})


def windshield_removal(request):
    return render(request, 'lidar/windshield-removal.html', {})
