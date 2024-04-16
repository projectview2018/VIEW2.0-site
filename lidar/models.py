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
    scan_status = models.TextField(default="uploaded")
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
    # full driver eye heights (seat height + sitting height)
    driver_eye_heights = models.CharField(
        validators=[validate_comma_separated_integer_list], max_length=2160, default="[0.0, 0.0, 0.0]")
    # 0 = lowest seat height, 1 = mid seat height, 2 = highest seat height
    driver_seat_heights = models.CharField(
        validators=[validate_comma_separated_integer_list], max_length=2160, default="[2, 1, 0]")
    # 0 = back-most seat position, 1 = mid seat position, 2 = forward-most seat position
    driver_seat_distances = models.CharField(
        validators=[validate_comma_separated_integer_list], max_length=2160, default="[2, 1, 0]")
    nvp_5th_female_xs = models.CharField(
        validators=[validate_comma_separated_integer_list], max_length=2160, default="[185, 186, 186, 194, 195, 195, 195, 198, 197, 200, 200, 202, 202, 202, 202, 203, 203, 203, 203, \
        203, 204, 203, 203, 203, 203, 214, 214, 215, 216, 214, 211, 213, 210, 210, 210, 219, 220, 221, 219, 217, 216, 215, 224, 222, 221, 220, 215, 215, 225, 224, 221, 220, 216, 226, \
            222, 221, 218, 214, 222, 219, 217, 213, 220, 217,212, 220, 216, 221, 216, 223, 232, 234, 234, 232, 232, 228, 235, 236, 228, 235, 228, 227, 225, 228, 229, 228, 225, 223, \
                225, 231, 228, 233, 237, 241, 247, 238, 239, 280, 272, 245, 236, 222, 203, 187, 170, 149, 116, 79, 57, 15, 1, -34, -61, -98, -124, -167, -190, -227, -263, -289, -313, \
                    -347, -382, -382, -430, -452, -483, -508, -536, -539]")
    nvp_5th_female_ys = models.CharField(
        validators=[validate_comma_separated_integer_list], max_length=2160, default="[-22, -15, -15, -18, -14, -14, -14, -12, -10, -9, -9, -7, -7, -7, -7, -4, -4, -4, -3, -3, 0, 2, 2, \
            2, 5, 7, 7, 9, 10, 11, 8, 13, 8, 14, 15, 16, 18, 21, 20, 23, 23, 23, 25, 27, 28, 28, 31, 31, 33, 37, 36, 37, 38, 41, 42, 46, 44, 46, 48, 50, 52, 51, 52, 55, 59, 61, 61, 69,\
                               67, 72, 77, 81, 81, 84, 90, 92, 94, 98, 104, 103, 107, 113, 120, 121, 132, 136, 141, 150, 153, 166, 172, 186, 202, 216, 235, 243, 265, 334, 351, 355, 356, \
                                391, 411, 425, 450, 450, 474, 476, 474, 476, 474, 475, 474, 501, 500, 500, 498, 497, 494, 495, 494, 492, 491, 464, 460, 458, 456, 453, 453, 428]")
    nvp_50th_male_xs = models.CharField(
        validators=[validate_comma_separated_integer_list], max_length=2160, default="[185, 186, 186, 194, 195, 195, 195, 198, 197, 200, 200, 202, 202, 202, 202, 203, 203, 203, 203, \
        203, 204, 203, 203, 203, 203, 214, 214, 215, 216, 214, 211, 213, 210, 210, 210, 219, 220, 221, 219, 217, 216, 215, 224, 222, 221, 220, 215, 215, 225, 224, 221, 220, 216, 226, \
            222, 221, 218, 214, 222, 219, 217, 213, 220, 217,212, 220, 216, 221, 216, 223, 232, 234, 234, 232, 232, 228, 235, 236, 228, 235, 228, 227, 225, 228, 229, 228, 225, 223, \
                225, 231, 228, 233, 237, 241, 247, 238, 239, 280, 272, 245, 236, 222, 203, 187, 170, 149, 116, 79, 57, 15, 1, -34, -61, -98, -124, -167, -190, -227, -263, -289, -313, \
                    -347, -382, -382, -430, -452, -483, -508, -536, -539]")
    nvp_50th_male_ys = models.CharField(
        validators=[validate_comma_separated_integer_list], max_length=2160, default="[-22, -15, -15, -18, -14, -14, -14, -12, -10, -9, -9, -7, -7, -7, -7, -4, -4, -4, -3, -3, 0, 2, 2, \
            2, 5, 7, 7, 9, 10, 11, 8, 13, 8, 14, 15, 16, 18, 21, 20, 23, 23, 23, 25, 27, 28, 28, 31, 31, 33, 37, 36, 37, 38, 41, 42, 46, 44, 46, 48, 50, 52, 51, 52, 55, 59, 61, 61, 69,\
                               67, 72, 77, 81, 81, 84, 90, 92, 94, 98, 104, 103, 107, 113, 120, 121, 132, 136, 141, 150, 153, 166, 172, 186, 202, 216, 235, 243, 265, 334, 351, 355, 356, \
                                391, 411, 425, 450, 450, 474, 476, 474, 476, 474, 475, 474, 501, 500, 500, 498, 497, 494, 495, 494, 492, 491, 464, 460, 458, 456, 453, 453, 428]")
    nvp_95th_male_xs = models.CharField(
        validators=[validate_comma_separated_integer_list], max_length=2160, default="[185, 186, 186, 194, 195, 195, 195, 198, 197, 200, 200, 202, 202, 202, 202, 203, 203, 203, 203, \
        203, 204, 203, 203, 203, 203, 214, 214, 215, 216, 214, 211, 213, 210, 210, 210, 219, 220, 221, 219, 217, 216, 215, 224, 222, 221, 220, 215, 215, 225, 224, 221, 220, 216, 226, \
            222, 221, 218, 214, 222, 219, 217, 213, 220, 217,212, 220, 216, 221, 216, 223, 232, 234, 234, 232, 232, 228, 235, 236, 228, 235, 228, 227, 225, 228, 229, 228, 225, 223, \
                225, 231, 228, 233, 237, 241, 247, 238, 239, 280, 272, 245, 236, 222, 203, 187, 170, 149, 116, 79, 57, 15, 1, -34, -61, -98, -124, -167, -190, -227, -263, -289, -313, \
                    -347, -382, -382, -430, -452, -483, -508, -536, -539]")
    nvp_95th_male_ys = models.CharField(
        validators=[validate_comma_separated_integer_list], max_length=2160, default="[-22, -15, -15, -18, -14, -14, -14, -12, -10, -9, -9, -7, -7, -7, -7, -4, -4, -4, -3, -3, 0, 2, 2, \
            2, 5, 7, 7, 9, 10, 11, 8, 13, 8, 14, 15, 16, 18, 21, 20, 23, 23, 23, 25, 27, 28, 28, 31, 31, 33, 37, 36, 37, 38, 41, 42, 46, 44, 46, 48, 50, 52, 51, 52, 55, 59, 61, 61, 69,\
                               67, 72, 77, 81, 81, 84, 90, 92, 94, 98, 104, 103, 107, 113, 120, 121, 132, 136, 141, 150, 153, 166, 172, 186, 202, 216, 235, 243, 265, 334, 351, 355, 356, \
                                391, 411, 425, 450, 450, 474, 476, 474, 476, 474, 475, 474, 501, 500, 500, 498, 497, 494, 495, 494, 492, 491, 464, 460, 458, 456, 453, 453, 428]")
    female_5th_area = models.FloatField(default=1000)
    male_50th_area = models.FloatField(default=1000)
    male_95th_area = models.FloatField(default=1000)
    vehicle_left = models.FloatField(default=0)
    vehicle_front = models.FloatField(default=0)
    vehicle_right = models.FloatField(default=0)
    vehicle_back = models.FloatField(default=0)
