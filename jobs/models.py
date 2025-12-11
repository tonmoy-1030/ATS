from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from candidates.models import Offer
from auditlog.registry import auditlog

class BusinessUnit(models.Model):
    
    BUSINESS_DIRECTOR = [
        ('Business Director (G-1)', 'Business Director (G-1)'),
        ('Business Director (G-2)', 'Business Director (G-2)'),
    ]
    
    name = models.CharField(max_length=255, unique=True)
    short_name = models.CharField(max_length=20, unique=True)
    floor_location = models.CharField(max_length=60)
    factory = models.CharField(max_length=255, blank=True, null=True)
    responsible_hr_manager_name = models.CharField(max_length=255, blank=True, null=True)
    responsible_hr_manager_designation = models.CharField(max_length=255, blank=True, null=True)
    business_director = models.CharField(max_length=255,choices= BUSINESS_DIRECTOR, blank=True, null=True)

    def __str__(self):
        return f"{self.name}"


class Job(models.Model):


    JOB_TYPES = [
        ('Replacement', 'Replacement'),
        ('New', 'New')
    ]
    
    job_title = models.CharField(max_length=255, null=False)
    department = models.CharField(max_length=255, null=False)
    unit = models.ForeignKey(BusinessUnit, models.CASCADE,  null=True, blank=True)
    job_location = models.CharField(max_length=255, null=False, blank=True)
    posting_date = models.DateField(null=False)
    types = models.CharField(max_length=255, choices=JOB_TYPES, null=False)
    no_of_position = models.IntegerField(null=False)
    google_sheet_id = models.CharField(max_length=255, null=True, blank=True)
    closing_date = models.DateField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    open_status = models.BooleanField(default=True)
        
    def filled_positions(self):
        return Offer.objects.filter(job=self, offer_status='Accepted').count()

    def available_positions(self):
        return self.no_of_position - self.filled_positions()
    
    def vacant_days(self):
        end_day = self.closing_date or timezone.now().date()
        if self.posting_date:
            start_day = min(self.posting_date, timezone.now().date())
            return (end_day - start_day).days
        else:
            return 0
    
    def save(self, *args, **kwargs):
        self.full_clean()  
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.id}, {self.unit.name}, {self.department}, {self.job_title}, {self.job_location}"

class InterviewSchedule(models.Model):

    interview_type = models.CharField(max_length=255, default='Initial', null=False)
    interview_date = models.DateTimeField(null=False, default=timezone.now)
    interviewer = models.ManyToManyField('employees.Employee')
    job = models.ManyToManyField(Job)
 
    def __str__(self):
        first_job = self.job.first() 
        if first_job:
            return f"{self.interview_type}, {self.interview_date}, {first_job.job_title}"
        else:
            return f"{self.interview_type}, {self.interview_date}, No Job Assigned"
   
class FinalInterviewSchedule(models.Model):
    interview_type = models.CharField(max_length=255, default='Final', null=False)
    interview_date = models.DateTimeField(null=False, default=timezone.now)
    interviewer = models.ManyToManyField('employees.Employee')
    job = models.ManyToManyField(Job)
 
    def __str__(self):
    
        first_job = self.job.first()
        if first_job:
            return f"{self.interview_type}, {self.interview_date}, {first_job.job_title}"
        else:
            return f"{self.interview_type}, {self.interview_date}, No Job Assigned" 


class SMSTemplate(models.Model):
    name = models.CharField(max_length=100, unique=True)
    template_type = models.CharField(max_length=50, default='Transactional')
    content = models.TextField(verbose_name="Template Content with Placeholders")
    form_link = models.URLField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name
    
class SMSLog(models.Model):
    recipient_number = models.CharField(max_length=15)
    message_content = models.TextField()
    sent_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=50)
    send_by = models.CharField(max_length=100)

    def __str__(self):
        return f"SMS to {self.recipient_number} at {self.sent_at} - Status: {self.status}"

auditlog.register(Job)
auditlog.register(InterviewSchedule)
auditlog.register(FinalInterviewSchedule)
auditlog.register(BusinessUnit)
auditlog.register(SMSTemplate)
auditlog.register(SMSLog)
