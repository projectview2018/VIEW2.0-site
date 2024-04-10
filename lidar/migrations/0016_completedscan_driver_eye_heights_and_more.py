# Generated by Django 5.0.3 on 2024-04-10 12:09

import django.core.validators
import re
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lidar', '0015_remove_completedscan_area_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='completedscan',
            name='driver_eye_heights',
            field=models.CharField(default='[0.0, 0.0, 0.0]', max_length=2160, validators=[django.core.validators.RegexValidator(re.compile('^\\d+(?:,\\d+)*\\Z'), code='invalid', message='Enter only digits separated by commas.')]),
        ),
        migrations.AddField(
            model_name='completedscan',
            name='driver_seat_distances',
            field=models.CharField(default='[2, 1, 0]', max_length=2160, validators=[django.core.validators.RegexValidator(re.compile('^\\d+(?:,\\d+)*\\Z'), code='invalid', message='Enter only digits separated by commas.')]),
        ),
        migrations.AddField(
            model_name='completedscan',
            name='driver_seat_heights',
            field=models.CharField(default='[2, 1, 0]', max_length=2160, validators=[django.core.validators.RegexValidator(re.compile('^\\d+(?:,\\d+)*\\Z'), code='invalid', message='Enter only digits separated by commas.')]),
        ),
    ]
