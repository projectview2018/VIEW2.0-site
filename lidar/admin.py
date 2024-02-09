from django.contrib import admin
from .models import Vehicle, Scan, CompletedScan


admin.site.register(Vehicle)
admin.site.register(Scan)
admin.site.register(CompletedScan)
