from django.db import models
from django.core.validators import validate_comma_separated_integer_list


BODY_CLASSES = ['N/A',
                'Passenger Cars',
                'Four Tire, Single Unit',
                'Buses',
                'Two Axle, Six Tire, Single Unit',
                'Three Axle, Single Unit',
                'Four or More Axle, Single Unit',
                'Four or Less Axle, Single Trailer',
                '5-Axle Tractor Semitrailer',
                'Six or More Axle, Single Trailer',
                'Five or Less Axle, Multi-Trailer',
                'Six Axle, Multi-Trailer',
                'Seven or More Axle, Multi-Trailer']


WEIGHT_CLASSES = ['Class 1', 'Class 2', 'Class 3',
                  'Class 4', 'Class 5', 'Class 6', 'Class 7', 'Class 8']


class Vehicle(models.Model):
    """
    Represents one type of vehicle

    Attributes:
        vehicle_added: a DateTime, the time when the vehicle was first added to
            the database
        vehicle_updated: a DateTime, the last time a CompletedScan was finished
            for this vehicle
        vehicle_make: a string, the make of the vehicle
        vehicle_model: a string, the model of the vehicle
        vehicle_year: an int, the year of the vehicle
        vehicle_body_class: an int between 1 and 13, the (1-indexed) index into
            BODY_CLASSES giving the body class for this vehicle
        vehicle_weight_class: an int between 1 and 8, the (1-indexed) index into
            WEIGHT_CLASSES giving the weight class for this vehicle
    """
    vehicle_added = models.DateTimeField(auto_now_add=True)
    vehicle_updated = models.DateTimeField(auto_now_add=True)
    vehicle_make = models.CharField(max_length=50)
    vehicle_model = models.CharField(max_length=50)
    vehicle_year = models.IntegerField()
    vehicle_body_class = models.IntegerField()
    vehicle_weight_class = models.IntegerField()

    def body_class(self) -> str:
        """
        Returns:
            a str, the name of the body class
        """
        return BODY_CLASSES[self.vehicle_body_class - 1]

    def weight_class(self) -> str:
        """
        Returns:
            a str, the name of the weight class
        """
        return WEIGHT_CLASSES[self.vehicle_weight_class - 1]

    def __str__(self) -> str:
        """
        Returns:
            a str, the common name for the vehicle (in year-make-model format)
        """
        return f'{self.vehicle_year} {self.vehicle_make} {self.vehicle_model}'


class Scan(models.Model):
    """
    The raw data associated with a single scan

    Args:
        vehicle: the Vehicle associated with this scan
        scan_added: the DateTime giving the time when this scan was added
        driver_side_start: a bool, True if the scan started on the driver side
        A_ft: an int, the number of feet for the A metric
        A_in: a float, the number of inches for the A metric
        B_ft: an int, the number of feet for the B metric
        B_in: a float, the number of inches for the B metric
        C_ft: an int, the number of feet for the C metric
        C_in: a float, the number of inches for the C metric
        D_ft: an int, the number of feet for the D metric
        D_in: a float, the number of inches for the D metric
        E_ft: an int, the number of feet for the E metric
        E_in: a float, the number of inches for the E metric
        F_ft: an int, the number of feet for the F metric
        F_in: a float, the number of inches for the F metric
        scan_status: a string, the status of the scan
        lidar_scan: a glb or gltf File containing the vehicle Scan
    """
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT)
    scan_added = models.DateTimeField(auto_now_add=True)
    driver_side_start = models.BooleanField()
    A_ft = models.IntegerField(default=0)
    A_in = models.FloatField(default=0)
    B_ft = models.IntegerField(default=0)
    B_in = models.FloatField(default=0)
    C_ft = models.IntegerField(default=0)
    C_in = models.FloatField(default=0)
    D_ft = models.IntegerField(default=0)
    D_in = models.FloatField(default=0)
    E_ft = models.IntegerField(default=0)
    E_in = models.FloatField(default=0)
    F_ft = models.IntegerField(default=0)
    F_in = models.FloatField(default=0)
    scan_status = models.TextField(default="uploaded")
    lidar_scan = models.FileField()

    @property
    def A_m(self) -> float:
        """
        Returns:
            a float, the A measurement in meters
        """
        return (self.A_ft * 12 + self.A_in * (-1 if self.A_ft < 0 else 1)) * 0.0254

    @property
    def B_m(self) -> float:
        """
        Returns:
            a float, the B measurement in meters
        """
        return (self.B_ft * 12 + self.B_in * (-1 if self.B_ft < 0 else 1)) * 0.0254

    @property
    def C_m(self) -> float:
        """
        Returns:
            a float, the C measurement in meters
        """
        return (self.C_ft * 12 + self.C_in * (-1 if self.C_ft < 0 else 1)) * 0.0254

    @property
    def D_m(self) -> float:
        """
        Returns:
            a float, the D measurement in meters
        """
        return (self.D_ft * 12 + self.D_in * (-1 if self.D_ft < 0 else 1)) * 0.0254

    @property
    def E_m(self) -> float:
        """
        Returns:
            a float, the E measurement in meters
        """
        return (self.E_ft * 12 + self.E_in * (-1 if self.E_ft < 0 else 1)) * 0.0254

    @property
    def F_m(self) -> float:
        """
        Returns:
            a float, the F measurement in meters
        """
        return (self.F_ft * 12 + self.F_in * (-1 if self.F_ft < 0 else 1)) * 0.0254


class CompletedScan(models.Model):
    raw_scan = models.ForeignKey(Scan, on_delete=models.PROTECT)
    completed_scan_added = models.DateTimeField(auto_now_add=True)
    # full driver eye heights (seat height + sitting height)
    driver_eye_heights = models.CharField(
        validators=[validate_comma_separated_integer_list], max_length=2160, default="[0, 0, 0]")
    # 0 = lowest seat height, 1 = mid seat height, 2 = highest seat height
    driver_seat_heights = models.CharField(
        validators=[validate_comma_separated_integer_list], max_length=2160, default="[2, 1, 0]")
    # 0 = back-most seat position, 1 = mid seat position, 2 = forward-most seat position
    driver_seat_distances = models.CharField(
        validators=[validate_comma_separated_integer_list], max_length=2160, default="[2, 1, 0]")
    nvp_5th_female_xs = models.CharField(
        validators=[validate_comma_separated_integer_list], max_length=2160, default="[]")
    nvp_5th_female_ys = models.CharField(
        validators=[validate_comma_separated_integer_list], max_length=2160, default="[]")
    nvp_50th_male_xs = models.CharField(
        validators=[validate_comma_separated_integer_list], max_length=2160, default="[]")
    nvp_50th_male_ys = models.CharField(
        validators=[validate_comma_separated_integer_list], max_length=2160, default="[]")
    nvp_95th_male_xs = models.CharField(
        validators=[validate_comma_separated_integer_list], max_length=2160, default="[]")
    nvp_95th_male_ys = models.CharField(
        validators=[validate_comma_separated_integer_list], max_length=2160, default="[]")
    female_5th_area = models.FloatField(default=-1)
    male_50th_area = models.FloatField(default=-1)
    male_95th_area = models.FloatField(default=-1)
    vehicle_left = models.FloatField(default=0)
    vehicle_front = models.FloatField(default=0)
    vehicle_right = models.FloatField(default=0)
    vehicle_back = models.FloatField(default=0)
