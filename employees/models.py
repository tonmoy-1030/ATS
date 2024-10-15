from django.db import models
from jobs.models import Job, BusinessUnit
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from dateutil.relativedelta import relativedelta
from django.utils import timezone


class ContactInfo(models.Model):
    profile_picture = models.URLField(max_length=255, null=True, blank=True)
    official_mobile = models.CharField(max_length=20, blank=True)
    emergency_contact_person = models.CharField(max_length=100, blank=True)
    emergency_contact_no = models.CharField(max_length=20, blank=True)
    emergency_person_address = models.CharField(max_length=100, blank=True)
    emer_relation_with_employee = models.CharField(max_length=100, blank=True, null=True)
    present_vill = models.CharField(max_length=100, blank=True)
    present_po = models.CharField(max_length=100, blank=True)
    present_ps = models.CharField(max_length=100, blank=True)
    present_dist = models.CharField(max_length=100, blank=True)
    permanent_vill = models.CharField(max_length=100, blank=True)
    permanent_po = models.CharField(max_length=100, blank=True)
    permanent_ps = models.CharField(max_length=100, blank=True)
    permanent_dist = models.CharField(max_length=100, blank=True)

    class Meta:
        abstract = True

class PersonalInfo(models.Model):
    date_of_birth = models.DateField(null=True, blank=True)
    blood_group = models.CharField(max_length=5, blank=True)
    father_name = models.CharField(max_length=100, blank=True)
    mother_name = models.CharField(max_length=100, blank=True)
    religion = models.CharField(max_length=100, blank=True)
    nid = models.CharField(max_length=20, blank=True)
    tin = models.CharField(max_length=20, blank=True)
    marital_status = models.CharField(max_length=10, blank=True)
    spouse_name = models.CharField(max_length=100, blank=True)
    no_of_son = models.CharField(max_length=100, null=True, blank=True)
    no_of_daughter = models.CharField(max_length=100, null=True, blank=True)
    

    class Meta:
        abstract = True

class Education(models.Model):
    highest_degree = models.CharField(max_length=100, blank=True)
    subject_highest_degree = models.CharField(max_length=100, blank=True)
    institution_highest_degree = models.CharField(max_length=100, blank=True)
    passing_year_highest_degree = models.CharField(max_length=100, null=True, blank=True)
    division_or_gpa_highest_degree = models.CharField(max_length=100, blank=True)
    professional_degree = models.CharField(max_length=100, blank=True)
    subject_professional_degree = models.CharField(max_length=100, blank=True)
    institution_professional_degree = models.CharField(max_length=100, blank=True)
    passing_year_professional_degree = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        abstract = True
        
class Nominee(models.Model):
    nominee_name = models.CharField(max_length=100, blank=True, null=True)
    nominee_father_name = models.CharField(max_length=100, blank=True, null=True)
    nominee_mohter_name = models.CharField(max_length=100, blank=True, null=True)
    nominee_mobile_no = models.CharField(max_length=100, blank=True, null=True)
    relation_with_employee = models.CharField(max_length=100, blank=True, null=True)
    nominee_nid = models.CharField(max_length=100, blank=True, null=True)
    nominee_vill = models.CharField(max_length=100, blank=True, null=True)
    nominee_po = models.CharField(max_length=100, blank=True, null=True)
    nominee_ps = models.CharField(max_length=100, blank=True, null=True)
    nominee_dist = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        abstract = True



class Employee(models.Model):
    
    BUSINESS_UNIT = [
        ('Consumer Division', 'Consumer'),
        ('T.K. Food Products Distribution Limited', 'T.K. Food'),
        ('Prime Pusti Limited', 'PPL'),
        ('Prime Cosmetics Limited', 'PCL'),
        ('Pusti Glory', 'Glory'),
    ]
    
    EID = models.CharField(max_length=10, null=True, unique=True,verbose_name='Employee ID')
    name = models.CharField(max_length=60, null=False, blank=False)
    designation = models.CharField(max_length=60, null=False, blank=False)
    department = models.CharField(max_length=60, null=False, blank=False)
    DOJ = models.DateField(blank=False, null=False, verbose_name='Date of Joining')
    job_location = models.CharField(max_length=255, null=False, blank=False, default="")
    mobile_no = models.CharField(max_length=60, null=False, blank=False, verbose_name='Mobile Number')
    email = models.EmailField(max_length=60, null=False, blank=False)
    unit = models.ForeignKey( BusinessUnit, on_delete=models.CASCADE, blank=False, null=False)
    confirmation_date = models.DateField(blank=False, null=False)
    active_status = models.BooleanField(default=True)
    candidate = models.OneToOneField("candidates.candidate", on_delete=models.CASCADE, null=True, blank=True)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, verbose_name='Job', null=True, blank=True)
    
    
    def save(self, *args, **kwargs):
        if not self.pk and not self.confirmation_date:
            self.confirmation_date = self.DOJ + relativedelta(months=6)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'
        
        

    def __str__(self):
        return f"{self.name} - {self.designation}-{self.department}-{self.unit}"
  
class EmployeeDetails(ContactInfo, PersonalInfo, Education, Nominee):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='details')

    class Meta:
        verbose_name = 'Employee Details'
        verbose_name_plural = 'Employee Details'  
        
    def __str__(self):
        return f"Employee Details for {self.employee}"
    
class SeperationStatus(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='seperation')
    resign_date = models.DateField(null=True, blank=True)
    reason = models.TextField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Separation Status'
        verbose_name_plural = 'Separation Statuses'
        

    def __str__(self):
        return f"Separation Status for {self.employee}"
    
    
@receiver(post_save, sender=SeperationStatus)
def update_employee_active_status(sender, instance, created, **kwargs):
    if created:
        instance.employee.active_status = False
        instance.employee.save()
        
@receiver(pre_delete, sender=SeperationStatus)
def update_employee_active_status(sender, instance, **kwargs):
    instance.employee.active_status = True
    instance.employee.save()

class EmployeeConfirmation(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="confirmation")
    issue_date = models.DateField(default=timezone.now)
    new_designation = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=100, choices=[('Confirmation', 'Confirmation'), ('Extension', 'Extension')], null=False)
    development_area = models.TextField(null=True, blank=True)
    effective_date = models.DateField(null=False)
    remarks = models.CharField(max_length=255, null=True, blank=True)
    reference_number = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.employee.EID}-{self.employee.name}"   
    
    def save(self, *args, **kwargs):
        if not self.issue_date:
            self.issue_date = timezone.now()
        if not self.reference_number:
            current_month = self.issue_date.month
            current_year = self.issue_date.year
            unit = self.employee.unit
            status = self.status

            max_reference_number = EmployeeConfirmation.objects.filter(
                issue_date__month=current_month,
                issue_date__year=current_year,
                employee__unit=unit,
                status = status
            ).aggregate(models.Max('reference_number'))['reference_number__max']

            self.reference_number = (max_reference_number or 0) + 1

        super().save(*args, **kwargs)
        
        if self.status == "Extension":
            self.employee.confirmation_date = self.effective_date + relativedelta(months=3)
        else:
            self.employee.confirmation_date = self.effective_date
        
        self.employee.save()

class TransferOrder(models.Model):
    LOCATION_CHOICES = [
        ("area", "Area"),
        ("region", "Region"),
        ("zone", "Zone"),
    ]
    NEW_LOCATION_CHOICES = [
        ("region", "Region"),
        ("zone", "Zone"),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="transfer")
    issue_date = models.DateField(default=timezone.now)
    current_job_location = models.CharField(max_length=100, null=False)
    current_location_type = models.CharField(max_length=100, choices=LOCATION_CHOICES, null=False)
    current_under_region_zone = models.CharField(max_length=100, null=True, blank=True)
    current_under_region_zone_type = models.CharField(max_length=100, choices=NEW_LOCATION_CHOICES, null=False, blank=True)
    new_job_location = models.CharField(max_length=100, null=False)
    new_location_type = models.CharField(max_length=100, choices=LOCATION_CHOICES, null=False)
    new_under_region_zone = models.CharField(max_length=100, null=True, blank=True)
    new_under_region_zone_type = models.CharField(max_length=100, choices=NEW_LOCATION_CHOICES, null=False, blank=True)
    new_designation = models.CharField(max_length=100, null=True, blank=True)
    report_to = models.CharField(max_length=255, null=False)
    effective_date = models.DateField(null=False, blank=False)
    reference_number = models.IntegerField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['employee', 'issue_date'], name='unique_entry')
        ]
    
    def __str__(self):
        return f"{self.employee.EID}-{self.employee.name}"  
    
    def save(self, *args, **kwargs):
        if not self.issue_date:
            self.issue_date = timezone.now()
        if not self.reference_number:
            current_month = self.issue_date.month
            current_year = self.issue_date.year
            unit = self.employee.unit

            max_reference_number = TransferOrder.objects.filter(
                issue_date__month=current_month,
                issue_date__year=current_year,
                employee__unit=unit,
            ).aggregate(models.Max('reference_number'))['reference_number__max']

            self.reference_number = (max_reference_number or 0) + 1

        super().save(*args, **kwargs)
        
        self.employee.job_location = self.new_job_location
        
        self.employee.save()
        
        
class PostingOrder(models.Model):
    LOCATION_CHOICES = [
        ("area", "Area"),
        ("region", "Region"),
        ("zone", "Zone"),
    ]
    NEW_LOCATION_CHOICES = [
        ("region", "Region"),
        ("zone", "Zone"),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="posting")
    issue_date = models.DateField(default=timezone.now)
    new_job_location = models.CharField(max_length=100, null=False)
    new_location_type = models.CharField(max_length=100, choices=LOCATION_CHOICES, null=False)
    new_under_region_zone = models.CharField(max_length=100, null=True, blank=True)
    new_under_region_zone_type = models.CharField(max_length=100, choices=NEW_LOCATION_CHOICES, null=True, blank=True)
    report_to = models.CharField(max_length=255, null=False)
    effective_date = models.DateField(null=False, blank=False)
    reference_number = models.IntegerField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['employee', 'issue_date'], name='unique_entry')
        ]
    
    def __str__(self):
        return f"{self.employee.EID}-{self.employee.name}"  
    
    def save(self, *args, **kwargs):
        if not self.issue_date:
            self.issue_date = timezone.now()
        if not self.reference_number:
            current_month = self.issue_date.month
            current_year = self.issue_date.year
            unit = self.employee.unit

            max_reference_number = PostingOrder.objects.filter(
                issue_date__month=current_month,
                issue_date__year=current_year,
                employee__unit=unit,
            ).aggregate(models.Max('reference_number'))['reference_number__max']

            self.reference_number = (max_reference_number or 0) + 1

        super().save(*args, **kwargs)
        
        self.employee.job_location = self.new_job_location
        
        self.employee.save()


class SalaryInfo(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE)
    issue_date = models.DateField(default=timezone.now)
    salary = models.IntegerField()
    report_to = models.CharField(max_length=255)
    place_of_posting = models.CharField(max_length=255, default="Dhaka")
    director_signature = models.CharField(max_length=255, default="Business Director (Group-1)", blank=True, null=True)
    CC1 = models.CharField(max_length=255, default="Business Director (Group-1)")
    CC2 = models.CharField(max_length=255, default="Business Director (Group-2)")
    CC3 = models.CharField(max_length=255, default="Head of Business")
    CC4 = models.CharField(max_length=255, null=True, blank=True)
    CC5 = models.CharField(max_length=255, null=True, blank=True)
    CC6 = models.CharField(max_length=255, default="Accounts Department")
    CC7 = models.CharField(max_length=255, null=True, default="Personal file")
    reference_number = models.IntegerField(blank=True, null=True)
    
    def __str__(self):
        return f'Salary info for {self.employee.name}'
    
    def save(self, *args, **kwargs):
        if not self.issue_date:
            self.issue_date = timezone.now()

        if self.reference_number is None:
            current_month = self.issue_date.month
            current_year = self.issue_date.year
            unit = self.employee.unit

            max_reference_number = SalaryInfo.objects.filter(
                issue_date__month=current_month,
                issue_date__year=current_year,
                employee__unit=unit
            ).aggregate(models.Max('reference_number'))['reference_number__max']

            self.reference_number = (max_reference_number or 0) + 1

        super().save(*args, **kwargs)
        
        # Update related employee record if necessary
        if hasattr(self.employee, 'save'):
            self.employee.save()