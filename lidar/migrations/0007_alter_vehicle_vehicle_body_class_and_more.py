# Generated by Django 5.0.2 on 2024-03-06 22:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("lidar", "0006_vehicle_vehicle_body_class_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="vehicle",
            name="vehicle_body_class",
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name="vehicle",
            name="vehicle_weight_class",
            field=models.IntegerField(),
        ),
    ]