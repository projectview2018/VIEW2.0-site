import trimesh
import numpy as np
from .models import Vehicle, Scan, CompletedScan


def complete_scan(scan: Scan, vehicle: Vehicle):
    print('Starting scan')
    mesh = trimesh.load(scan.lidar_scan.path, force='mesh')
    print('Loading scan')
    eye_pos = np.array([scan.eye_x_m, scan.eye_y_m, scan.eye_z_m])
    nvp_xs, nvp_ys = find_nvps(mesh, eye_pos, scan.driver_side_start)
    print('Found NVPs')
    coordinates = np.stack([nvp_xs, nvp_ys]).T
    coordinates = np.concatenate([np.zeros((1, 2)), coordinates])
    completed_scan = CompletedScan(
        raw_scan=scan,
        nvp_xs=nvp_xs,
        nvp_ys=nvp_ys,
        area=calculate_area(coordinates)
    )
    print('Created new CompletedScan model')
    completed_scan.save()
    print('Saved scan')
    vehicle.vehicle_updated = completed_scan.completed_scan_added
    print('Updated vehicle\'s time stamp')
    vehicle.save()
    print('Vehicle\'s time stamp saved')


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
    # face by point by (x, y, z) (F x 3 x 3 matrix)
    faces_by_points = mesh.vertices[mesh.faces, :]
    print('Ran face by points')
    # face by (x, y, z) (F x 3 matrix) - the highest point on each face
    high_point = np.array([max(points, key=lambda p: p[1])
                           for points in faces_by_points])
    print('Found high point')
    # The directions to cast rays
    yaws = np.deg2rad(np.arange(70, 200) + (0 if driver_side_start else 180))
    pitches = np.deg2rad(np.arange(-85, -5))
    print('Found desired pitches and yaws')
    yawgrid, pitchgrid = np.meshgrid(yaws, pitches)
    print('Created mesh grid')
    ray_angles = np.stack((yawgrid.flatten(), pitchgrid.flatten())).T
    print('Stacked ray angles')
    # An (n x 3) matrix of unit vectors in each direction (given yaw and pitch)
    rays = np.array([
        np.sin(ray_angles[:, 0]) * np.cos(ray_angles[:, 1]),
        np.sin(ray_angles[:, 1]),
        np.cos(ray_angles[:, 0]) * np.cos(ray_angles[:, 1]),
    ]).T
    print('Put rays in an array')
    # An (n x 3) matrix where each row is equal to eye_pos
    eye_pos_repeated = np.tile(eye_pos, rays.shape[0]).reshape((-1, 3))
    print('Created eye pos matrix')
    # Perform raycasts
    intersections = mesh.ray.intersects_first(eye_pos_repeated, rays)
    print('Raycasts performed')
    # For each yaw, find the tallest face that any of the rays intersect
    face_idxs_by_yaw = np.zeros((yaws.size,), dtype=int)
    for idx, yaw in enumerate(yaws):
        faces = intersections[ray_angles[:, 0] == yaw]
        face_idxs_by_yaw[idx] = int(
            max(faces, key=lambda f: -10000 if f == -1 else high_point[f, 1]))
    print('Ray intersections found')
    # The height of the ground (the lowest point in the entire mesh)
    floor_y_val = np.min(mesh.vertices[:, 1])
    print('Found height of the floor')
    # A (y x 3) matrix - the direction of the NVP in a given yaw
    nvp_rays = (high_point[face_idxs_by_yaw, :] - eye_pos).T
    print('Found NVP rays for given yaw')
    # Calculate the vector which points from eye position to NVP
    hypot = np.sqrt(np.sum(nvp_rays * nvp_rays, axis=0))
    nvp_rays /= hypot  # Normalize
    nvp_rays *= -(eye_pos[1] - floor_y_val) / \
        nvp_rays[1, :]  # scale until ground hit
    nvp_rays *= 100
    nvp_rays = np.floor(nvp_rays)
    if driver_side_start:
        nvp_rays *= -1
    print('Vectors calculated, NVPS found')
    return [-int(x) for x in nvp_rays[0, :]], [int(y) for y in nvp_rays[2, :]]


def calculate_area(coordinates):
    # Code adapted from https://stackoverflow.com/questions/41077185/fastest-way-to-shoelace-formula
    x = coordinates[:, 0]
    y = coordinates[:, 1]

    S1 = np.sum(x * np.roll(y, -1))
    S2 = np.sum(y * np.roll(x, -1))

    area = .5 * np.absolute(S1 - S2)

    return area
