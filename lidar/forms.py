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
            'A_ft': forms.TextInput(attrs={
                'type': 'number',
                'min': "0",
                'name': "front-to-front (ft) input",
                'step': "1",
                'required': "true",
                'placeholder': "000",
                'class': "data-upload-textinput03 Body input elevation01",
            }),
            'A_in': forms.TextInput(attrs={
                'type': "number",
                'min': "0",
                'name': "front-to-front (in) input",
                'required': "true",
                'placeholder': "00.00",
                'class': "data-upload-textinput04 Body input elevation01",
            }),
            'B_ft': forms.TextInput(attrs={
                'type': "number",
                'min': "0",
                'name': "front-to-back (ft) input",
                'step': "1",
                'required': "true",
                'placeholder': "000",
                'class': "data-upload-textinput05 Body input elevation01",
            }),
            'B_in': forms.TextInput(attrs={
                'type': "number",
                'min': "0",
                'name': "front-to-back (in) input",
                'required': "true",
                'placeholder': "00.00",
                'class': "data-upload-textinput06 Body input elevation01",
            }),
            'C_ft': forms.TextInput(attrs={
                'type': "number",
                'min': "0",
                'name': "seat depth (ft) input",
                'step': "1",
                'required': "true",
                'placeholder': "000",
                'class': "data-upload-textinput07 Body input elevation01",
            }),
            'C_in': forms.TextInput(attrs={
                'type': "number",
                'min': "0",
                'name': "seat depth (in) input",
                'required': "true",
                'placeholder': "00.00",
                'class': "data-upload-textinput08 Body input elevation01",
            }),
            'D_ft': forms.TextInput(attrs={
                'type': "number",
                'min': "0",
                'name': "seat center distance (ft) input",
                'step': "1",
                'required': "true",
                'placeholder': "000",
                'class': "data-upload-textinput09 Body input elevation01",
            }),
            'D_in': forms.TextInput(attrs={
                'type': "number",
                'min': "0",
                'name': "seat center distance (in) input",
                'required': "true",
                'placeholder': "00.00",
                'class': "data-upload-textinput10 Body input elevation01",
            }),
            'E_ft': forms.TextInput(attrs={
                'type': "number",
                'min': "0",
                'name': "seat high (ft) input",
                'step': "1",
                'required': "true",
                'placeholder': "000",
                'class': "data-upload-textinput11 Body input elevation01",
            }),
            'E_in': forms.TextInput(attrs={
                'type': "number",
                'min': "0",
                'name': "seat high (in) input",
                'required': "true",
                'placeholder': "00.00",
                'class': "data-upload-textinput12 Body input elevation01",
            }),
            'F_ft': forms.TextInput(attrs={
                'type': "number",
                'min': "0",
                'name': "seat low (ft) input",
                'step': "1",
                'required': "true",
                'placeholder': "000",
                'class': "data-upload-textinput13 Body input elevation01",
            }),
            'F_in': forms.TextInput(attrs={
                'type': "number",
                'min': "0",
                'name': "seat low (in) input",
                'required': "true",
                'placeholder': "00.00",
                'class': "data-upload-textinput14 Body input elevation01",
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
        fields = ['driver_side_start', 'A_ft', 'A_in', 'B_ft', 'B_in', 'C_ft', 'C_in', 'D_ft', 'D_in',
                  'E_ft', 'E_in', 'F_ft', 'F_in', 'lidar_scan']
