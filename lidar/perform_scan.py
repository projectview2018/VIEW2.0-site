"""
Module for calculating blindzone information
"""

import trimesh
import numpy as np
from .models import Scan, CompletedScan
from .s3_utils import get_object


def complete_scan(scan: Scan):
    """
    Create and save a CompletedScan object for the given scan

    Load the mesh from the file manager and perform raycasting on it for each
    height of driver. Save this data into a CompletedScan object in the
    database, along with body information and area calculations. Update the
    timestamps for the scan and its associated vehicle.

    Args:
        scan: the Scan to create a CompletedScan object from
    """
    print(f'scan_path: {scan.lidar_scan.name}')
    scan.scan_status = "calculating"
    scan.save()

    # Get recently uploaded scan from the bucket
    response = get_object(scan.lidar_scan.name)

    print('Starting scan')
    mesh: trimesh.Trimesh = trimesh.load(response['Body'], file_type='gltf', force='mesh')
    print('Loading scan')
    del response

    vehicle_front_left, vehicle_back_right = get_vehicle_bounding_box(
        mesh, scan.driver_side_start)
    if not scan.driver_side_start:  # If passenger side, FL is max, BR is min
        vehicle_front_left, vehicle_back_right = vehicle_back_right, vehicle_front_left

    # array of information for 5th female, 50th male, 95th male , respectively [m]
    driver_sitting_heights = np.array(
        [69.8, 80.4, 86]) * 0.01  # convert from cm to m
    # high, mid, low [m]
    driver_seat_heights = np.array(
        [scan.E_m, (scan.E_m + scan.F_m) / 2, scan.F_m])
    # forward, mid, back [m]
    driver_seat_positions = np.array(
        [scan.A_m, (scan.B_m + scan.A_m) / 2, scan.B_m]) + scan.C_m
    driver_eye_heights = []  # list to hold total eye heights for each driver height

    # list to hold all six sets of nvps for three driver heights
    list_of_nvps = []
    # list to hold all areas for three driver heights
    list_of_areas = []
    for height_index in range(len(driver_sitting_heights)):
        print(f"calculating nvps for height #{height_index+1}")
        # assuming mid track and mid-height for future calculations
        # eye pos in front-left frame, using scan-frame axes
        eye_x_m = scan.D_m
        eye_y_m = driver_seat_heights[height_index] + \
            driver_sitting_heights[height_index]
        eye_z_m = driver_seat_positions[height_index]
        driver_eye_heights.append(eye_y_m)
        eye_pos = np.array([eye_x_m, eye_y_m, eye_z_m])
        scan_eye_pos = get_eye_in_mesh_frame(
            mesh, eye_pos, scan.driver_side_start)

        # Calculate NVPs
        nvp_xs, nvp_ys = find_nvps(mesh, scan_eye_pos, scan.driver_side_start)
        print(f"Found NVPs for height #{height_index+1}")
        list_of_nvps.append(nvp_xs)
        list_of_nvps.append(nvp_ys)
        coordinates = np.stack([nvp_xs, nvp_ys]).T
        coordinates = np.concatenate([np.zeros((1, 2)), coordinates])
        list_of_areas.append(calculate_area(coordinates))
    del mesh

    completed_scan = CompletedScan(
        raw_scan=scan,
        driver_eye_heights=list(driver_eye_heights),
        driver_seat_heights=list(driver_seat_heights),
        driver_seat_distances=list(driver_seat_positions),
        nvp_5th_female_xs=list_of_nvps[0],
        nvp_5th_female_ys=list_of_nvps[1],
        nvp_50th_male_xs=list_of_nvps[2],
        nvp_50th_male_ys=list_of_nvps[3],
        nvp_95th_male_xs=list_of_nvps[4],
        nvp_95th_male_ys=list_of_nvps[5],
        female_5th_area=list_of_areas[0],
        male_50th_area=list_of_areas[1],
        male_95th_area=list_of_areas[2],
        vehicle_left=vehicle_front_left[0],
        vehicle_front=vehicle_front_left[2],
        vehicle_right=vehicle_back_right[0],
        vehicle_back=vehicle_back_right[2],
    )
    print('Created new CompletedScan model')
    completed_scan.save()
    print('Saved completed scan to database')
    scan.vehicle.vehicle_updated = completed_scan.completed_scan_added
    print('Updated vehicle\'s time stamp')
    scan.vehicle.save()
    print('Vehicle\'s time stamp saved')
    scan.scan_status = "processed"
    scan.save()


def find_nvps(mesh: trimesh.primitives.Trimesh, eye_pos: np.ndarray,
              driver_side_start: bool) -> tuple[list[int], list[int]]:
    """
    Calculate the NVPs from a given eye position for a given mesh

    Args:
        mesh: the Trimesh giving the vertices and faces of the vehicle mesh
        eye_pos: a 3D NumPy vector giving the coordinates of the eye position
        driver_side_start: a bool, True when the scan started on the driver
            side of the car, False when the scan started on the passenger side.

    Returns:
        a tuple of two int lists of equivalent length, giving the x-coordinates
        and y-coordinates of the NVPs, respectively
    """
    # The directions to cast rays
    yaws = np.deg2rad(np.arange(70, 290, 2) +
                      (0 if driver_side_start else 180))
    pitches = np.deg2rad(np.arange(-85, -1, 2))
    print('Found desired pitches and yaws')

    # An (p x 3) matrix where each row is equal to eye_pos
    eye_pos_repeated = np.tile(eye_pos, pitches.shape[0]).reshape((-1, 3))
    print('Created eye pos matrix')

    # The height of the ground (the lowest point in the entire mesh)
    floor_y_val = np.min(mesh.vertices[:, 1])
    print('Found height of the floor')

    nvp_rays = np.zeros((yaws.shape[0], 3))
    for idx, yaw in enumerate(yaws):
        # An (n x 3) matrix of unit vectors in each direction (given yaw and pitch)
        rays = np.array([
            np.sin(yaw) * np.cos(pitches),
            np.sin(pitches),
            np.cos(yaw) * np.cos(pitches),
        ]).T

        # Perform raycasts
        intersections = mesh.ray.intersects_first(eye_pos_repeated, rays)
        face_idx_vals = intersections[intersections >= 0]

        if face_idx_vals.size > 0:
            # Find the ray that hits the floor at the furthest distance
            faces = mesh.faces[face_idx_vals, :]
            face_vertices = mesh.vertices[faces, :]
            highest_face_vertices = face_vertices[np.arange(
                faces.shape[0]), np.argmax(face_vertices[:, :, 1], axis=1), :]
            initial_rays = highest_face_vertices - eye_pos
            initial_rays = initial_rays[initial_rays[:, 1] < 0, :]
            rays_to_floor = initial_rays * \
                (floor_y_val - eye_pos[1]) / \
                initial_rays[:, 1].reshape((-1, 1))
            nvp_rays[idx, :] = rays_to_floor[np.argmax(
                np.linalg.norm(rays_to_floor[:, (0, 2)], axis=1)), :]
            print(f'Found NVP for yaw {yaw:.3f}: {nvp_rays[idx, :]}')
        else:
            nvp_rays[idx, :] = np.nan
            print(f'No NVP found for yaw: {yaw:.3f}')

    nvp_rays = nvp_rays[~np.isnan(nvp_rays)].reshape((-1, 3))

    # Convert to cm, int
    nvp_rays *= 100
    nvp_rays = np.floor(nvp_rays)
    if driver_side_start:
        nvp_rays *= -1
    print('Vectors calculated, NVPS found')

    return [-int(x) for x in nvp_rays[:, 0]], [int(y) for y in nvp_rays[:, 2]]


def calculate_area(coordinates: np.ndarray) -> float:
    """
    Calculate the area of a shape bounded by the given coordinates

    Uses the shoelace formula to calculate area. Code adapted from
    https://stackoverflow.com/questions/41077185/fastest-way-to-shoelace-formula

    Args:
        coordinates: an (n x 2) NumPy vector giving the X-Y vertices of the
            shape to calculate the area of

    Returns:
        a float, the area of the shape defined by coordinates
    """
    x = coordinates[:, 0]
    y = coordinates[:, 1]

    S1 = np.sum(x * np.roll(y, -1))
    S2 = np.sum(y * np.roll(x, -1))

    area = .5 * np.absolute(S1 - S2)
    return area


def get_vehicle_bounding_box(mesh: trimesh.Trimesh, driver_start: bool)\
        -> tuple[np.ndarray, np.ndarray]:
    """
    Calculate the bounding box of a vehicle scan, excluding side mirrors

    Filters out all points within 0.5 meters of the lowest point and find the
    minimum and maximum XYZ points of the filtered points. Takes the points
    which have the highest and lowest x-values as the side mirrors. For each,
    it adds 0.25 meters to the Z coordinate to ensure the mirrors are not in
    frame, and adjusts the minimum and maximum X value to be the min/max in
    this new filtered view. If the resulting Z cutoff is more than 70% of the
    way from the front to the back of the scan, it is assumed the mirror was
    not in the scan and the original X position is used instead

    Args:
        mesh: the Trimesh scan representing a car to find the bounding box of
        driver_start: a bool, True if the scan started on the driver's side of
            the car, False otherwise

    Returns:
        a tuple of two 3D NumPy vectors giving the X/Y/Z of the minimum and
            maximum bounds of the car, respectively
    """
    # Filter out the ground
    min_height = np.min(mesh.vertices[:, 1])
    vertices = mesh.vertices[mesh.vertices[:, 1] > min_height + 0.5, :]

    # Flip the X and Z axes if its a passenger side scan
    passenger_side_adj = np.array([-1, 1, -1])
    if not driver_start:
        vertices *= passenger_side_adj

    # Find the original guesses at the bounding box
    min_pos = np.min(vertices, axis=0)
    min_pos[1] = min_height
    max_pos = np.max(vertices, axis=0)

    # Find the Z values of the point with the min and max X value
    min_idx = np.argmin(vertices, axis=0)
    max_idx = np.argmax(vertices, axis=0)
    z_of_min_x = vertices[min_idx[0], 2]
    z_of_max_x = vertices[max_idx[0], 2]

    # Find the minimum X value of all points with Z greater than the cutoff
    # If the cutoff is too close to the back of the car, use the original Z
    min_percent = (z_of_min_x - min_pos[2]) / (max_pos[2] - min_pos[2])
    if min_percent < 0.7:
        filtered_by_min = vertices[vertices[:, 2] > z_of_min_x + 0.25, :]
    else:
        filtered_by_min = vertices
    min_pos[0] = np.min(filtered_by_min[:, 0])

    # Find the maximum X value of all points with Z greater than the cutoff
    # If the cutoff is too close to the back of the car, use the original Z
    max_percent = (z_of_max_x - min_pos[2]) / (max_pos[2] - min_pos[2])
    if max_percent < 0.7:
        filtered_by_max = vertices[vertices[:, 2] > z_of_max_x + 0.25, :]
    else:
        filtered_by_max = vertices
    max_pos[0] = np.max(filtered_by_max[:, 0])

    # Readjust everything if the scan was the passenger side of the car
    if not driver_start:
        min_pos *= passenger_side_adj
        max_pos *= passenger_side_adj
        bounds = np.stack([min_pos, max_pos])
        min_pos = np.min(bounds, axis=0)
        max_pos = np.max(bounds, axis=0)
    return min_pos, max_pos


def get_eye_in_mesh_frame(mesh: trimesh.Trimesh, eye_pos: np.ndarray,
                          driver_start: bool) -> np.ndarray:
    """
    Convert an eye position from front-left of car frame to mesh frame

    Finds the bounding box of the car (without side mirrors) and adds the
    X/Z values from the front left of the car to the given eye_pos

    Args:
        mesh: a Trimesh object, the scan of the car to adjust the eye pos in
        eye_pos: a 3D NumPy vector, the eye position in FL frame to convert
        driver_start: a bool, True if the scan started on the driver's side of
            the car, False otherwise

    Returns:
        a 3D NumPy vector, the eye position in the same frame as the mesh
    """
    if not driver_start:
        eye_pos *= np.array([-1, 1, -1])
    min_pos, max_pos = get_vehicle_bounding_box(mesh, driver_start)
    z_front = (min_pos if driver_start else max_pos)[2]
    x_left = (min_pos if driver_start else max_pos)[0]
    new_eye_pos = [eye_pos[0] + x_left,
                   eye_pos[1] + min_pos[1], eye_pos[2] + z_front]
    return np.array(new_eye_pos)
