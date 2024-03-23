# Generated by Django 5.0.3 on 2024-03-14 20:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lidar', '0007_alter_vehicle_vehicle_body_class_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scan',
            name='eye_x_ft',
        ),
        migrations.RemoveField(
            model_name='scan',
            name='eye_x_in',
        ),
        migrations.RemoveField(
            model_name='scan',
            name='eye_y_ft',
        ),
        migrations.RemoveField(
            model_name='scan',
            name='eye_y_in',
        ),
        migrations.RemoveField(
            model_name='scan',
            name='eye_z_ft',
        ),
        migrations.RemoveField(
            model_name='scan',
            name='eye_z_in',
        ),
        migrations.AddField(
            model_name='scan',
            name='A_ft',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='scan',
            name='A_in',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='scan',
            name='B_ft',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='scan',
            name='B_in',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='scan',
            name='C_ft',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='scan',
            name='C_in',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='scan',
            name='D_ft',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='scan',
            name='D_in',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='scan',
            name='E_ft',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='scan',
            name='E_in',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='scan',
            name='F_ft',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='scan',
            name='F_in',
            field=models.FloatField(default=0),
        ),
    ]