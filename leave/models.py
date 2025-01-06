from django.db import models
from django.utils import timezone
from employees.models import Employee
from django.core.exceptions import ValidationError
from auditlog.registry import auditlog


class Holiday(models.Model):
    date = models.DateField(unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} - {self.date}"

class LeaveType(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name
    

class LeaveAllocation(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    year = models.IntegerField(default=timezone.now().year)  # The year for which the leave is allocated
    leave_allocated = models.IntegerField()  # Total leaves allocated for the year
    leave_taken = models.FloatField(default=0)  # Leaves already taken
    leave_balance = models.FloatField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['employee', 'leave_type', 'year'], name='unique_leave_allocation')
        ]

    def __str__(self):
        return f"{self.employee} - {self.leave_type} ({self.year})"
    

    def clean(self):
        # Ensure leave taken does not exceed leave allocated
        if self.leave_taken > self.leave_allocated:
            raise ValidationError("Leave taken cannot exceed allocated leave.")

    def save(self, *args, **kwargs):
        # Update leave balance before saving
        self.update_leave_balance()
        super().save(*args, **kwargs)

    def update_leave_balance(self):
        # Calculate leave balance
        self.leave_balance = self.leave_allocated - self.leave_taken
        if self.leave_balance < 0:
            raise ValidationError("Leave taken cannot exceed allocated leave.")

    def __str__(self):
        return f"{self.employee.name} - {self.leave_type} from {self.year}"
    

class LeaveApplication(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    total_days = models.FloatField(default=0)
    remarks = models.CharField(max_length=255, null=True, blank=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['employee', 'start_date', 'end_date'], name='unique_leave_application')
        ]

    def clean(self):
        overlapping_requests = LeaveApplication.objects.filter(
            employee=self.employee,
            start_date__lte=self.end_date,
            end_date__gte=self.start_date,
        ).exclude(id=self.id)

        if overlapping_requests.exists():
            raise ValidationError("Date is already exist.")
        
        
    def save(self, *args, **kwargs):
        self.clean()  # Ensure clean() is called to check for validation errors

        # Retrieve the allocation for the year and leave type
        allocation = LeaveAllocation.objects.get(employee=self.employee, leave_type=self.leave_type, year=self.start_date.year)

        # Check if this is an update or a new record
        if self.pk:
            # If updating, calculate the difference in days
            old_instance = LeaveApplication.objects.get(pk=self.pk)
            days_difference = self.total_days - old_instance.total_days
        else:
            days_difference = self.total_days

        # Check if the requested leave exceeds the available balance
        if allocation.leave_taken + days_difference > allocation.leave_allocated:
            raise ValidationError("Leave request exceeds the available leave balance.")

        # Update the leave taken
        allocation.leave_taken += days_difference
        allocation.update_leave_balance()
        allocation.save()

        super().save(*args, **kwargs)

    
    def __str__(self):
        return f"{self.employee.name} - {self.leave_type} from {self.start_date} to {self.end_date}"

auditlog.register(Holiday)
auditlog.register(LeaveType)
auditlog.register(LeaveAllocation)
auditlog.register(LeaveApplication)
