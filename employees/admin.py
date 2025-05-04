from django.contrib import admin
from .models import (Employee, EmployeeDetails, SeperationStatus, 
                     EmployeeConfirmation, TransferOrder, PostingOrder, SalaryInfo)

# Register your models here.
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('EID', 'name', 'designation', 'department', 'unit', 'email', 'mobile_no')
    search_fields = ('EID', 'name')
    list_filter = ('department', 'unit')
    ordering = ('EID',)

@admin.register(EmployeeDetails)
class EmployeeDetailsAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date_of_birth', 'marital_status', 'blood_group')
    search_fields = ('employee__name', 'employee__EID')
    ordering = ('employee__EID',)

@admin.register(SeperationStatus)
class SeperationStatusAdmin(admin.ModelAdmin):
    list_display = ('employee', 'resign_date', 'reason')
    search_fields = ('employee__name', 'employee__EID')
    ordering = ('resign_date',)

@admin.register(EmployeeConfirmation)
class EmployeeConfirmationAdmin(admin.ModelAdmin):
    list_display = ('employee', 'effective_date', 'remarks')
    search_fields = ('employee__name', 'employee__EID')
    ordering = ('effective_date',)

@admin.register(TransferOrder)
class TransferOrderAdmin(admin.ModelAdmin):
    list_display = ('employee',  'effective_date')
    search_fields = ('employee__name', 'employee__EID')
    ordering = ('effective_date',)

@admin.register(PostingOrder)
class PostingOrderAdmin(admin.ModelAdmin):
    list_display = ('employee',  'effective_date')
    search_fields = ('employee__name', 'employee__EID')
    ordering = ('effective_date',)

@admin.register(SalaryInfo)
class SalaryInfoAdmin(admin.ModelAdmin):
    list_display = ('employee', 'salary')
    search_fields = ('employee__name', 'employee__EID')
    ordering = ('-employee__DOJ',)

