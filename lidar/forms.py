from django import forms
from .models import Scan, Vehicle


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        body_classes = ['N/A',
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
        body_classes_dict = {i + 1: body_class for i,
                             body_class in enumerate(body_classes)}

        weight_classes = ['Class 1', 'Class 2', 'Class 3',
                          'Class 4', 'Class 5', 'Class 6', 'Class 7', 'Class 8']
        weight_classes_dict = {i + 1: weight_class for i,
                               weight_class in enumerate(weight_classes)}

        widgets = {
            'vehicle_body_class': forms.Select(
                attrs={
                    'name': "Scan start side selector",
                    'required': "true",
                    'class': "data-upload-select elevation01",
                },
                choices=body_classes_dict,
            ),
            'vehicle_weight_class': forms.Select(
                attrs={
                    'name': "Scan start side selector",
                    'required': "true",
                    'class': "data-upload-select1 elevation01",
                },
                choices=weight_classes_dict,
            ),
            'vehicle_make': forms.TextInput(
                attrs={
                    'type': "text",
                    'name': "vehicle make input",
                    'required': "true",
                    'placeholder': "Toyota",
                    'class': "data-upload-textinput Body input elevation01",
                },
            ),
            'vehicle_model': forms.TextInput(
                attrs={
                    'type': "text",
                    'name': "vehicle model input",
                    'required': "true",
                    'placeholder': "Corolla",
                    'class': "data-upload-textinput01 Body input elevation01",
                }
            ),
            'vehicle_year': forms.NumberInput(
                attrs={
                    'type': "number",
                    'max': "2099",
                    'min': "1900",
                    'name': "Vehicle Year (model year)",
                    'step': "1",
                    'required': "true",
                    'placeholder': "2015",
                    'class': "data-upload-textinput02 Body input elevation01",
                }
            )
        }
        fields = ['vehicle_body_class', 'vehicle_weight_class',
                  'vehicle_make', 'vehicle_model', 'vehicle_year']


class ScanForm(forms.ModelForm):
    class Meta:
        model = Scan

        start_side_dict = {
            True: 'Driver Side',
            False: 'Passenger Side'
        }

        widgets = {
            'driver_side_start': forms.Select(
                attrs={
                    'name': "Scan start side selector",
                    'required': "true",
                    'class': "data-upload-select2 elevation01",
                },
                choices=start_side_dict,
            ),
            'eye_y_ft': forms.TextInput(attrs={
                'class': 'data-upload-textinput Body input',
                'type': 'text',
                'name': 'eye height (ft) input',
                'required': 'true',
                'placeholder': '000'
            }),
            'eye_y_in': forms.TextInput(attrs={
                'type': 'text',
                'name': 'eye height (in) input',
                'required': 'true',
                'placeholder': '00.00',
                'class': 'data-upload-textinput1 Body input'
            }),
            'eye_z_ft': forms.TextInput(attrs={
                'type': "text",
                'name': "eye to hood distance (ft) input",
                'required': "true",
                'placeholder': "000",
                'class': "data-upload-textinput2 Body input"
            }),
            'eye_z_in': forms.TextInput(attrs={
                'type': "text",
                'name': "eye to hood distance (in) input",
                'required': "true",
                'placeholder': "00.00",
                'class': "data-upload-textinput3 Body input",
            }),
            'eye_x_ft': forms.TextInput(attrs={
                'type': "text",
                'name': "eye to door distance (ft) input",
                'required': "true",
                'placeholder': "000",
                'class': "data-upload-textinput4 Body input",
            }),
            'eye_x_in': forms.TextInput(attrs={
                'type': "text",
                'name': "eye to door distance (in) input",
                'required': "true",
                'placeholder': "00.00",
                'class': "data-upload-textinput5 input Body",
            }),
            'lidar_scan': forms.FileInput(attrs={
                'type': "file",
                'id': "lidar-file-selector",
                'name': "LiDAR Scan File Selector",
                'required': "true",
                'placeholder': "placeholder",
                'class': "data-upload-textinput6 Body input",
            }),
        }
        fields = ['driver_side_start', 'vehicle', 'eye_x_ft', 'eye_x_in',
                  'eye_y_ft', 'eye_y_in', 'eye_z_ft', 'eye_z_in', 'lidar_scan']
