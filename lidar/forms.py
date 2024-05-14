from django import forms
from .models import Scan, Vehicle, BODY_CLASSES, WEIGHT_CLASSES


class VehicleForm(forms.ModelForm):
    """
    Form for the user to input the type of vehicle they are uploading
    """
    class Meta:
        """
        Metadata for the VehicleForm

        Attributes:
            model: a class, the output type of the form (a Vehicle)
            body_classes: a list of strings, the options for the dropdown
                determining the body class of the vehicle
            body_classes_dict: a dict mapping ints to strings, the IDs for each
                body class to the name of the body class
            weight_classes: a list of strings, the options for the dropdown
                determining the weight class of the vehicle
            weight_classes_dict: a dict mapping ints to strings, the IDs for
                each weight class to the name of the weight class
            widgets: a dict mapping strings to form inputs, the name of the
                Vehicle attribute to the form input for that attribute
            fields: a list of strings, the names of the Vehicle attributes that
                are set by this form (the keys in widgets)
        """
        model = Vehicle
        body_classes = BODY_CLASSES
        body_classes_dict = {i + 1: body_class for i,
                             body_class in enumerate(body_classes)}

        weight_classes = WEIGHT_CLASSES
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
    """
    Form for the user to input the scan they are uploading
    """
    class Meta:
        """
        Metadata for the ScanFrom

        Attributes:
            model: a class, the output type of the form (a Scan)
            start_side_dict: a dict mapping bools to strings, where the keys
                are the stored data and the values are the displayed names for
                the driver_side_start attribute
            widgets: a dict mapping strings to form inputs, the name of the
                Scan attribute to the form input for that attribute
            fields: a list of strings, the names of the Scan attributes that
                are set by this form (the keys in widgets)
        """
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


class VisualizationForm(forms.Form):
    """
    Form for the user to select the type of plot they want to make

    Attributes:
        VRUS: a list of tuples, where each tuple gives 1) the ID of the VRU (a
            numeric string) and 2) the displayed text for the VRU (a string)
        eye_positions: a list of tuples, where each tuple gives 1) the ID of
            the eye position (a numeric string) and 2) the displayed text for
            the eye position (a string)
        vru_selected: a MultipleChoiceField for the user to select the VRU(s)
            to visualize
        eye_position_selected: a MultipleChoiceField for the user to select the
            eye position to visualize
    """
    VRUS = [
        ("1", 'Preschool child (28 inches)'),
        ("2", 'Elementary school child on bicycle (35 inches)'),
        ("3", 'Elementary school child (37 inches)'),
        ("4", 'Wheelchair user (39 inches)'),
        ("5", 'Adult on bicycle (47 inches)'),
        ("6", 'Adult (49 inches)'),
    ]
    eye_positions = [
        ("1", "5th-Percentile Female (60 inches)"),
        ("2", "50th-Percentile Male (69 inches)"),
        ("3", "95th-Percentile Male (74 inches)"),
    ]

    vru_selected = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(),
        choices=VRUS,)
    eye_position_selected = forms.ChoiceField(
        widget=forms.RadioSelect(),
        choices=eye_positions,
    )
