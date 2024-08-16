from django.contrib import admin
from .models import (Employee, EmployeeDetails, SeperationStatus, 
                     EmployeeConfirmation, TransferOrder, PostingOrder, SalaryInfo)

# Register your models here.
admin.site.register(Employee)
admin.site.register(EmployeeDetails)
admin.site.register(SeperationStatus)
admin.site.register(EmployeeConfirmation)
admin.site.register(TransferOrder)
admin.site.register(PostingOrder)
admin.site.register(SalaryInfo)


