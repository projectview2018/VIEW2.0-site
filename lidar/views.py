from django.shortcuts import render
from django.http import HttpResponseRedirect
import threading
from .forms import ScanForm
from .perform_scan import complete_scan
from .models import Vehicle, Scan, CompletedScan


def index(request):
    return render(request, 'lidar/index.html', {})


def add_vehicle(request):
    return render(request, 'lidar/add-vehicle.html', {})


def data_upload(request):
    if request.method == 'POST':
        form = ScanForm(request.POST, request.FILES)
        if form.is_valid():
            scan = form.save()
            thread = threading.Thread(target=complete_scan, args=(scan,))
            thread.start()
            return HttpResponseRedirect('/add_vehicle')
    else:
        form = ScanForm()
    return render(request, 'lidar/data-upload.html', {'form': form})


def faq(request):
    return render(request, 'lidar/faq.html', {})


def vehicle_database_loading(request):
    return render(request, 'lidar/vehicle-database-loading.html', {})


def vehicle_database_table(request):
    vehicle_list = Vehicle.objects.all()
    # scan_list = Scan.objects.all()
    # completed_scan_list = CompletedScan.objects.all()

    return render(request, 'lidar/vehicle-database-table.html',
                  {'vehicle_list': vehicle_list})
