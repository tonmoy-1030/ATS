from django.contrib import admin
from .models import LeaveAllocation, LeaveApplication, LeaveType, Holiday

# Register your models here.
admin.site.register(LeaveAllocation)
admin.site.register(LeaveApplication)
admin.site.register(LeaveType)
admin.site.register(Holiday)
