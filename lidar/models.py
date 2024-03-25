from django.db import models
from django.core.validators import validate_comma_separated_integer_list


class Vehicle(models.Model):
    vehicle_added = models.DateTimeField(auto_now_add=True)
    vehicle_updated = models.DateTimeField(auto_now_add=True)
    vehicle_make = models.CharField(max_length=50)
    vehicle_model = models.CharField(max_length=50)
    vehicle_year = models.IntegerField()
    # body class - int field 1-13
    vehicle_body_class = models.IntegerField()
    # weight class - int field 1-8
    vehicle_weight_class = models.IntegerField()

    def __str__(self) -> str:
        return f'{self.vehicle_year} {self.vehicle_make} {self.vehicle_model}'


class Scan(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT)
    scan_added = models.DateTimeField(auto_now_add=True)
    driver_side_start = models.BooleanField()
    # eye_x_ft = models.IntegerField(default=0)
    # eye_x_in = models.FloatField(default=0)
    # eye_y_ft = models.IntegerField(default=0)
    # eye_y_in = models.FloatField(default=0)
    # eye_z_ft = models.IntegerField(default=0)
    # eye_z_in = models.FloatField(default=0)
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
    lidar_scan = models.FileField()

    # @property
    # def eye_x_m(self) -> float:
    #     return (self.eye_x_ft * 12 + self.eye_x_in * (-1 if self.eye_x_ft < 0 else 1)) * 0.0254

    # @property
    # def eye_y_m(self) -> float:
    #     return (self.eye_y_ft * 12 + self.eye_y_in * (-1 if self.eye_y_ft < 0 else 1)) * 0.0254

    # @property
    # def eye_z_m(self) -> float:
    #     return (self.eye_z_ft * 12 + self.eye_z_in * (-1 if self.eye_z_ft < 0 else 1)) * 0.0254

    @property
    def A_m(self) -> float:
        return (self.A_ft * 12 + self.A_in * (-1 if self.A_ft < 0 else 1)) * 0.0254

    @property
    def B_m(self) -> float:
        return (self.B_ft * 12 + self.B_in * (-1 if self.B_ft < 0 else 1)) * 0.0254

    @property
    def C_m(self) -> float:
        return (self.C_ft * 12 + self.C_in * (-1 if self.C_ft < 0 else 1)) * 0.0254

    @property
    def D_m(self) -> float:
        return (self.D_ft * 12 + self.D_in * (-1 if self.D_ft < 0 else 1)) * 0.0254

    @property
    def E_m(self) -> float:
        return (self.E_ft * 12 + self.E_in * (-1 if self.E_ft < 0 else 1)) * 0.0254

    @property
    def F_m(self) -> float:
        return (self.F_ft * 12 + self.F_in * (-1 if self.F_ft < 0 else 1)) * 0.0254


class CompletedScan(models.Model):
    raw_scan = models.ForeignKey(Scan, on_delete=models.PROTECT)
    completed_scan_added = models.DateTimeField(auto_now_add=True)
    nvp_xs = models.CharField(
        validators=[validate_comma_separated_integer_list], max_length=2160)
    nvp_ys = models.CharField(
        validators=[validate_comma_separated_integer_list], max_length=2160)
    area = models.FloatField()
