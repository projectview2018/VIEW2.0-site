import json
from django.core import serializers
from .models import Vehicle, Scan, CompletedScan
from .s3_utils import generate_presigned_url_get, generate_presigned_url_put
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.utils import timezone
import threading
from .forms import ScanForm, VehicleForm, VisualizationForm
from .perform_scan import complete_scan
from .plot_visualizations import viz_overhead
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET


def index(request):
    """
    A view function that returns the homepage of the website, where users can read about direct vision, the website, and its users.

    Args:
        request: an HttpRequest object requesting for the page to be loaded, generated by Django automatically
    Returns:
        An HttpResponse object with content for the homepage, outputted by a call to the render function
    """
    return render(request, 'lidar/index.html', {})


def faq(request):
    """
    A view function that returns the FAQ page of the website, where users can find commonly asked questions and their answers.

    Args:
        request: an HttpRequest object requesting for the page to be loaded, generated by Django automatically
    Returns:
        An HttpResponse object with content for the FAQ page, outputted by a call to the render function
    """
    return render(request, 'lidar/faq.html', {})


def add_vehicle(request):
    """
    A view function that returns the Add Vehicle page of the website, where users can either find instructions to measure a vehicle,
    or be redirected tot he page to upload data to the data-table.

    Args:
        request: an HttpRequest object requesting for the page to be loaded, generated by Django automatically
    Returns:
        An HttpResponse object with content for the Add Vehicle page, outputted by a call to the render function
    """
    return render(request, 'lidar/add-vehicle.html', {})


def instructions(request):
    """
    A view function that returns the Measurement Instructions page of the website, where users can either find instructions to measure
    and take a lidar scan of a vehicle.

    Args:
        request: an HttpRequest object requesting for the page to be loaded, generated by Django automatically
    Returns:
        An HttpResponse object with content for the Measurement Instructions page, outputted by a call to the render function
    """
    return render(request, 'lidar/instructions.html', {})


def data_upload(request):
    """
    A view function that returns the Data Upload page of the website, where users can directly inout vehicle information, measurements,
    and their lidar scan.

    Args:
        request: an HttpRequest object requesting for the page to be loaded, generated by Django automatically
    Returns:
        IF NO form is successfully submitted,
            An HttpResponse object with content for the Data Upload page, outputted by a call to the render function
        IF form successfully submitted,
            An HttpResponseRedirect to the Window Removal page

    """
    # if a form was submitted
    if request.method == 'POST':
        # print("request was a POST")
        vehicle_form = VehicleForm(request.POST, request.FILES)
        scan_form = ScanForm(request.POST, request.FILES)
        # print(f'scan form errors: {scan_form.errors}')
        # print(f'vehicle form errors: {vehicle_form.errors}')

        # if both scan form and vehicle forms are complete and have valid data
        if scan_form.is_valid() and vehicle_form.is_valid():
            # get vehicle data, but don't push to database yet
            vehicle = vehicle_form.save(commit=False)

            # check if the same vehicle already exists in the database (CASE SENSITIVE); if it does, update the last time a scan for that
            # vehicle was uploaded; if it doesn't, create a new vehicle (obj) with the form information and upload it to the database
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
            # print("vehicle query successful")

            # get scan data, but don't push to database yet
            scan = scan_form.save(commit=False)
            # created is True if new Vehicle object was made, so assign to Scan object
            if created:
                print("vehicle not found: assigning new vehicle to scan")
                scan.vehicle = obj
                print(
                    f"new vehicle, {obj.vehicle_make} {obj.vehicle_model} {obj.vehicle_year}, saved")
            # created is False if Vehicle already existed, so find Vehicle in database and assign to Scan object
            else:
                print("vehicle found: assigning old vehicle to scan")
                vehicle = Vehicle.objects.get(
                    vehicle_make=vehicle.vehicle_make, vehicle_model=vehicle.vehicle_model, vehicle_year=vehicle.vehicle_year)
                scan.vehicle = vehicle
                print(
                    f"previous vehicle, {vehicle.vehicle_make} {vehicle.vehicle_model} {vehicle.vehicle_year}, updated")
            # Upload Scan object to database
            scan.save()
            print("scan form saved")
            # redirect to Window Removal page once Scan and Vehicle successfully uploaded to database and available for further processing
            return HttpResponseRedirect(f'/windshield_removal/{scan.id}')
    # if no form was submitted
    else:
        vehicle_form = VehicleForm()
        scan_form = ScanForm()
    return render(request, 'lidar/data-upload.html', {'scan_form': scan_form, 'vehicle_form': vehicle_form})


def windshield_removal(request, scan_id):
    """
    A view function that returns the Window Removal page after a user has inputted information about a Vehicle, where they must next
    erase the windshield, and driver and passenger windows from the lidar scan.

    Args:
        request: an HttpRequest object requesting for the page to be loaded, generated by Django automatically
    Returns:
        An HttpResponse object with content for the WIndow Removal page, outputted by a call to the render function
    """
    # search inside the Spaces bucket for the scan just uploaded on the previous Data Upload page
    scan = Scan.objects.get(pk=scan_id)
    scan_file = scan.lidar_scan
    print(f"scan_status upon window removal: {scan.scan_status}")
    # possible statuses the scan can be after finishing window removal and hitting the "Submit Entry" button
    post_windshield_strings = {"modified", "calculating", "processed"}
    # if entering the window removal page straight from the data upload page, update the scan status to "modifying"
    if scan.scan_status == "uploaded":
        scan.scan_status = "modifying"
        scan.save()
    elif (scan.scan_status in post_windshield_strings):
        # if clean, modified scan already submitted, do not allow user to go back to page
        print(
            "Scan already modified and cleaned, cannot go back to windshield_removal page.")
        return render(request, 'lidar/404.html', {})

    # print(f'Got scan_file: {scan_file}, {type(scan_file)}')
    scan_path = scan_file.name
    print(f'{scan_path = }')
    # create urls to get and put objects in the DO Spaces bucket when needed
    get_url = generate_presigned_url_get(scan_path)
    put_url = generate_presigned_url_put(scan_path)
    return render(request, 'lidar/windshield-removal.html',
                  {'scan_id': scan_id, 'scan_path': scan_path, 'get_url': get_url, 'put_url': put_url})


def vehicle_database_loading(request):
    """
    A view function that returns the loading page that appears after the user has uploaded Vehicle and Measurement information along
    with a scan, and while the backend is calculating NVPs for the three drivers.

    Args:
        request: an HttpRequest object requesting for the page to be loaded, generated by Django automatically
    Returns:
        An HttpResponse object with content for the loading page, outputted by a call to the render function
    """
    return render(request, 'lidar/vehicle-database-loading.html', {})


def vehicle_database_table(request):
    """
    A view function that returns the Vehicle Database page of the website, where users can find a table containing Vehicles already
    measured and their various scans and associated visualizations.

    Args:
        request: an HttpRequest object requesting for the page to be loaded, generated by Django automatically
    Returns:
        An HttpResponse object with content for the vehicle Database page, outputted by a call to the render function
    """
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
    """
    A view function that returns the Blindzone Visualizations page for a selected vehicle scan.

    Args:
        request: an HttpRequest object requesting for the page to be loaded, generated by Django automatically
        scan_id (int): The id of the selected scan inside the database
    Returns:
        An HttpResponse object with content for the Add Vehicle page, outputted by a call to the render function
    """
    # find the scan that matches the scan_id (there are no scans with the same id)
    scan = Scan.objects.get(pk=scan_id)
    # get the make, model, and year of the scan's associated vehicle to be displayed on the page
    vehicle = scan.vehicle
    make = vehicle.vehicle_make
    model = vehicle.vehicle_model
    year = vehicle.vehicle_year

    viz_form = VisualizationForm()
    # create a thread name that will be used for NVP calculation of the selected vehicle later
    thread_name = f'process-scan-{scan_id}'
    print(f"Scan status on load: {scan.scan_status}")
    # visualization page automatically attempted to be loaded after erasing windows is finished on the Window removal page, so the status
    # of the scan must be updated from "modifying" (user in still in process of erasing windows) to "modified" (windows are removed but
    # NVP calculation has not begun)
    if scan.scan_status == "modifying":
        scan.scan_status = "modified"
        scan.save()
    # once window removal is complete, start a new thread that will calculate NVPs
    if scan.scan_status == "modified":
        print("Tried to load Visualization page. Scan about to be processed.")
        # start thread in which NVP calculation for the selected scan is done
        thread = threading.Thread(
            target=complete_scan, args=(scan, vehicle), name=thread_name)
        thread.start()
        return render(request, 'lidar/visualization.html', {'VisualizationForm': viz_form, 'scan_id': scan_id, 'make': make, 'model': model, 'year': year, 'date': scan.scan_added, 'graph': None, 'vrus_selected': None, "closest_forward_nvps": None, "num_vrus_in_vru_nvp_area": None, "loading": True})
    # onces calculation has begun inside thread, in which the scan's status is updated to "calculating", check on calculation process
    # for any crashes and restart process if a crash occurs
    if scan.scan_status == "calculating":
        # initially assume calculation is happening
        performing_scan = False
        # search among currently active threads for the thread handling NVP calculation for selected scan
        for thread in threading.enumerate():
            # if thread found, scan calculation is being performed, update performing_scan variable, and stop searching
            if thread.name == thread_name:
                performing_scan = True
                break
        # if thread with with intended name not found, while scan status is supposed to be "calculating", then a crash occurred, the
        # thread was lost, and a new thread with the same name must be made
        if not performing_scan:
            print(
                f'Lost thread {thread_name} while calculating. Restarting...')
            thread = threading.Thread(
                target=complete_scan, args=(scan, vehicle), name=thread_name)
            thread.start()

        print("Tried to load Visualization page. Scan is still being processed.")
        return render(request, 'lidar/visualization.html', {'VisualizationForm': viz_form, 'scan_id': scan_id, 'make': make, 'model': model, 'year': year, 'date': scan.scan_added, 'graph': None, 'vrus_selected': None, "closest_forward_nvps": None, "num_vrus_in_vru_nvp_area": None, "loading": True})

    # once calculating is done, scan status should be updated to "processed" inside the thread, then visualization page should be loaded
    if scan.scan_status == "processed":
        num_completed_scans = CompletedScan.objects.filter(
            raw_scan=scan).count()

        # check that a CompletedScan object associated with the selected scan exists, and if so, check for a form submission
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

                    # load appropriate NVPs based on user's selected driver height
                    if (eye_pos == 1):
                        nvp_xs = json.loads(completed_scan.nvp_5th_female_xs)
                        nvp_ys = json.loads(completed_scan.nvp_5th_female_ys)
                    elif (eye_pos == 2):
                        nvp_xs = json.loads(completed_scan.nvp_50th_male_xs)
                        nvp_ys = json.loads(completed_scan.nvp_50th_male_ys)
                    else:
                        nvp_xs = json.loads(completed_scan.nvp_95th_male_xs)
                        nvp_ys = json.loads(completed_scan.nvp_95th_male_ys)

                    # load driver information to be accessed
                    driver_eye_heights = json.loads(
                        completed_scan.driver_eye_heights)
                    driver_seat_positions = json.loads(
                        completed_scan.driver_seat_distances)

                    # grab driver information for user's selected driver height
                    # height of selected driver's eye from the ground
                    eye_height_full = driver_eye_heights[eye_pos-1]
                    # distance of selected driver's eye from hood
                    eye_point_full = driver_seat_positions[eye_pos-1]

                    # vehicle width in [ft]
                    vehicle_width = abs(
                        completed_scan.vehicle_left - completed_scan.vehicle_right) * 3.28084
                    # latitudinal distance from driver's eye to outside of the vehicle on driver's side in [ft]
                    vehicle_D = scan.D_ft + (scan.D_in / 12)

                    # call the function to generate the plot image, and relevant statistics for each user-selected VRU
                    graph, closest_forward_nvps, num_vrus_in_vru_nvp_area = viz_overhead(
                        nvp_xs, nvp_ys, eye_height_full, eye_point_full, eye_pos, vrus_selected, vehicle_width, vehicle_D)
                    return render(request, 'lidar/visualization.html', {'VisualizationForm': viz_form, 'scan_id': scan_id, 'make': make, 'model': model, 'year': year, 'date': scan.scan_added, 'graph': graph, 'vrus_selected': vrus_selected, "closest_forward_nvps": closest_forward_nvps, "num_vrus_in_vru_nvp_area": num_vrus_in_vru_nvp_area, "loading": False})

            return render(request, 'lidar/visualization.html', {'VisualizationForm': viz_form, 'scan_id': scan_id, 'make': make, 'model': model, 'year': year, 'date': scan.scan_added, 'graph': None, 'vrus_selected': None, "closest_forward_nvps": None, "num_vrus_in_vru_nvp_area": None, "loading": False})

        print("Tried to load Visualization page. Scan should be processed, some error occurred.")
        return render(request, 'lidar/404.html', {})


@require_GET
@cache_control(max_age=60 * 60 * 24, immutable=True, public=True)  # one day
def favicon(request):
    return HttpResponse(
        (
            '<?xml version="1.0" encoding="UTF-8"?><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 74.73 51.32"><defs><style>.c{fill:#1a6ea7;}</style></defs><g id="a"/><g id="b"><path class="c" d="M19.2,0H0C11.24,10.82,19.53,26.42,23.05,44.47c3.56-11.92,7.75-21.66,12.65-29.29C31.19,8.55,25.77,3.19,19.2,0ZM10.25,2.29h2.63c1.68,1.02,3.26,2.19,4.75,3.5h-2.92c-1.4-1.29-2.88-2.47-4.47-3.5Zm5.72,4.71h2.99c1.84,1.77,3.53,3.78,5.11,5.97h-3.26c-1.47-2.15-3.07-4.17-4.84-5.97Zm11.08,17.93c-.98-2.45-2.06-4.84-3.28-7.11l-.92-1.65c-.3-.51-.62-1.01-.93-1.51h3.33c.33,.5,.68,.99,1,1.51,0,0,1,1.64,1.01,1.66l.02,.04s1.14,2.03,1.69,3.08c-.65,1.28-1.29,2.61-1.91,3.98Z"/><path class="c" d="M55.53,0c-16.61,8.07-25.88,29.93-31.54,51.32h26.59C53.16,30.39,62.08,12.17,74.73,0h-19.2Z"/></g></svg>'
        ),
        content_type="image/svg+xml",
    )
