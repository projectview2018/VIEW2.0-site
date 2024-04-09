import trimesh
import numpy as np
from .models import Vehicle, Scan, CompletedScan
from .s3_utils import create_s3_client


def complete_scan(scan: Scan, vehicle: Vehicle):
    print(f'scan_path: {scan.lidar_scan.name}')
    scan.scan_status = "calculating"
    scan.save()
    # create s3 client to  access digital ocean space bucket
    s3_client = create_s3_client()

    # Get recently uploaded scan from the bucket
    response = s3_client.get_object(
        Bucket='vehicle-scans', Key=f'media/lidar/lidar_scans/{scan.lidar_scan.name}')

    print('Starting scan')
    # print(f"scan before changing to binary: {response['Body'].read()}")
    mesh = trimesh.load(response['Body'], file_type='gltf', force='mesh')
    print('Loading scan')
    driver_heights = np.array([60.0, 69.0, 74.0]) * 0.0254
    list_of_nvps = []  # list to hold all six sets of nvps for three driver heights
    # list to hold all three coordinates to calculate areas for three driver heights
    list_of_coordinates = []
    # driver_height = 1.2
    height_index = 1
    for driver_height in driver_heights:
        print(f"calculating nvps for height #{height_index}")
        # assuming mid track and mid-height for future calculations
        eye_x_m = scan.D_m
        eye_y_m = scan.A_m - ((scan.B_m - scan.A_m) / 2)
        eye_z_m = scan.F_m + ((scan.E_m - scan.F_m) / 2) + driver_height
        eye_pos = np.array([eye_x_m, eye_y_m, eye_z_m])
        # eye_pos = np.array([scan.eye_x_m, scan.eye_y_m, scan.eye_z_m])
        nvp_xs, nvp_ys = find_nvps(mesh, eye_pos, scan.driver_side_start)
        print(f"Found NVPs for height #{height_index}")
        list_of_nvps.append(nvp_xs)
        list_of_nvps.append(nvp_ys)
        coordinates = np.stack([nvp_xs, nvp_ys]).T
        coordinates = np.concatenate([np.zeros((1, 2)), coordinates])
        list_of_coordinates.append(coordinates)
        height_index += 1

    completed_scan = CompletedScan(
        raw_scan=scan,
        nvp_5th_female_xs=list_of_nvps[0],
        nvp_5th_female_ys=list_of_nvps[1],
        nvp_50th_male_xs=list_of_nvps[2],
        nvp_50th_male_ys=list_of_nvps[3],
        nvp_95th_male_xs=list_of_nvps[4],
        nvp_95th_male_ys=list_of_nvps[5],
        female_5th_area=calculate_area(list_of_coordinates[0]),
        male_50th_area=calculate_area(list_of_coordinates[1]),
        male_95th_area=calculate_area(list_of_coordinates[2]),
    )
    # print('Saving original scan')
    # scan.save()
    print('Created new CompletedScan model')
    completed_scan.save()
    print('Saved completed scan to database')
    vehicle.vehicle_updated = completed_scan.completed_scan_added
    print('Updated vehicle\'s time stamp')
    vehicle.save()
    print('Vehicle\'s time stamp saved')
    scan.scan_status = "processed"
    scan.save()


def find_nvps(mesh: trimesh.primitives.Trimesh, eye_pos: np.ndarray,
              driver_side_start: bool):
    """
    Calculate the NVPs from a given eye position for a given mesh

    :param mesh: the Trimesh giving the vertices and faces of the vehicle mesh
    :param eye_pos: a 3D numpy vector giving the coordinates of the eye position
    :param driver_side_start: a bool, True when the scan started on the driver
        side of the car, False when the scan started on the passenger side.
    :return: a tuple of two numpy vectors of equivalent length, giving the
        x-coordinates and y-coordinates of the NVPs, respectively
    """
    # The directions to cast rays
    yaws = np.deg2rad(np.arange(70, 200) +
                      (0 if driver_side_start else 180))
    pitches = np.deg2rad(np.arange(-85, -1))
    print('Found desired pitches and yaws')

    # An (p x 3) matrix where each row is equal to eye_pos
    eye_pos_repeated = np.tile(eye_pos, pitches.shape[0]).reshape((-1, 3))
    print('Created eye pos matrix')

    nvp_rays = np.zeros((yaws.shape[0], 3))
    for idx, yaw in enumerate(yaws):
        # An (n x 3) matrix of unit vectors in each direction (given yaw and pitch)
        rays = np.array([
            np.sin(yaw) * np.cos(pitches),
            np.sin(pitches),
            np.cos(yaw) * np.cos(pitches),
        ]).T
        print('Put rays in an array')

        # Perform raycasts
        intersections = mesh.ray.intersects_first(eye_pos_repeated, rays)
        print(f'Raycasts performed for yaw: {yaw}')
        face_idx_vals = intersections[intersections >= 0]

        if face_idx_vals.size > 0:
            face_idx = face_idx_vals[-1]
            face = mesh.faces[face_idx, :]
            face_vertices = mesh.vertices[face, :]
            highest_vertex_idx = np.argmax(face_vertices[:, 1])
            highest_vertex = mesh.vertices[face[highest_vertex_idx]]
            nvp_rays[idx, :] = (highest_vertex - eye_pos)
        else:
            nvp_rays[idx, :] = np.nan

    nvp_rays = nvp_rays[~np.isnan(nvp_rays)].reshape((-1, 3))

    # The height of the ground (the lowest point in the entire mesh)
    floor_y_val = np.min(mesh.vertices[:, 1])
    print('Found height of the floor')

    # Calculate the vector which points from eye position to NVP
    hypot = np.sqrt(np.sum(nvp_rays * nvp_rays, axis=0))
    nvp_rays /= hypot  # Normalize
    nvp_rays *= -(eye_pos[1] - floor_y_val) / \
        np.stack([nvp_rays[:, 1]] * 3).T  # scale until ground hit
    nvp_rays *= 100
    nvp_rays = np.floor(nvp_rays)
    if driver_side_start:
        nvp_rays *= -1
    print('Vectors calculated, NVPS found')
    return [-int(x) for x in nvp_rays[:, 0]], [int(y) for y in nvp_rays[:, 2]]


def calculate_area(coordinates):
    # Code adapted from https://stackoverflow.com/questions/41077185/fastest-way-to-shoelace-formula
    x = coordinates[:, 0]
    y = coordinates[:, 1]

    S1 = np.sum(x * np.roll(y, -1))
    S2 = np.sum(y * np.roll(x, -1))

    area = .5 * np.absolute(S1 - S2)

    return area


# def correct_mesh_frame(mesh):
#     x_coordinates = mesh.vertices[:, 0]
#     y_coordinates = mesh.vertices[:, 1]
#     z_coordinates = mesh.vertices[:, 2]

#     ground_z = np.min(z_coordinates)
#     ground_range = 0.5  # m off the ground within which to remove points from mesh
#     filt_ground = z_coordinates > (ground_z + ground_range)

#     final_vertices = mesh.vertices[filt_ground]

#     left_mirror
