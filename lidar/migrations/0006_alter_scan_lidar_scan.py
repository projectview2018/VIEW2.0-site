# Generated by Django 5.0.1 on 2024-03-05 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lidar', '0005_vehicle_vehicle_updated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scan',
            name='lidar_scan',
            field=models.FileField(upload_to='lidar/lidar_scans/'),
        ),
    ]
