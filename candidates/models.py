from django.db import models
import phonenumbers
from django.utils import timezone
from django.core.exceptions import ValidationError
from auditlog.registry import auditlog


class CandidateInitialInformation(models.Model):
        name = models.CharField(max_length=255, null=True, blank=True)
        mobile_no = models.CharField(max_length=255, null=True, blank=True)
        email = models.CharField(max_length=255, null=True, blank=True)
        highest_education_degree = models.CharField(max_length=255, null=True, blank=True)
        highest_education_degree_institution = models.CharField(max_length=255, null=True, blank=True)
        professional_education_degree = models.CharField(max_length=255, null=True, blank=True)
        passing_year = models.CharField(max_length=255, null=True, blank=True)
        experience = models.JSONField(null=True, blank=True)
        address = models.TextField(null=True, blank=True)
        total_experience = models.CharField(max_length=255, null=True, blank=True)
        current_designation= models.CharField(max_length=255, null=True, blank=True)
        current_organization = models.CharField(max_length=255, null=True, blank=True)
        current_location = models.CharField(max_length=255, null=True, blank=True)
        resume = models.FileField(upload_to='resumes/', null=True, blank=True)
        upload_date = models.DateTimeField(auto_now_add=True)
        status = models.CharField(choices=(('New', 'New'), ('shortlisted', 'shortlisted'), ('rejected', 'rejected')), max_length=20, default='New')
        jobs = models.ManyToManyField("jobs.Job",related_name="initial_applications", blank=True )
       
        def __str__(self):
            try:
                job = self.jobs.first() if hasattr(self, "jobs") else None
                return f"{self.name}-{self.mobile_no}-{job.title if job else 'No Job'}"
            except Exception as e:
                return f"{self.name}-{self.mobile_no}-Error: {e}"


class Candidate(models.Model):
    ATTENDANCE_STATUS = [
        ('Absent','Absent'),
        ('Present', 'Present')
    ]
    
    INITIAL_INTERVIEW_STATUS = [
        ('Deferred','Deferred'),
        ('Waiting', 'Waiting'),
        ('Forwarding for the next Interivew','Forwarding for the next Interivew'),
        ('immediate Recruitment', "immediate Recruitment")
        
    ]

    FINAL_INTERVIEW_STATUS = [
        ('Deferred','Deferred'),
        ('Waiting', 'Waiting'),
        ('Immediate Recruitment', "Immediate Recruitment")
        
    ]
    
    PHONE_CONFIRMATION_CHOICES  = [
        ('Confirmed', 'Confirmed'),
        ('Not Interested', 'Not Interested'),
        ('Unable to Attend', 'Unable to Attend'),
        ('Call Not Received', 'Call Not Received'),
        ('Phone Switched Off', 'Phone Switched Off'),
        ('Interested in Next Schedule', 'Interested in Next Schedule'),
        ('Previously Interviewed', 'Previously Interviewed'),
        ('Wrong Number', 'Wrong Number'),
        ('Salary Not Matched', 'Salary Not Matched'),
    ]

    name = models.CharField(max_length=255)
    mobile = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    filename = models.CharField(max_length=255)
    attendance_status = models.CharField(max_length=255, choices=ATTENDANCE_STATUS, default='Absent')
    invitation_status = models.CharField(max_length=255, choices=PHONE_CONFIRMATION_CHOICES, default='Confirmed', null=True, blank=True)
    initial_interview_status = models.CharField(max_length=255, choices=INITIAL_INTERVIEW_STATUS, null=True, blank=True)
    final_interview_attendance = models.CharField(max_length=255, choices=ATTENDANCE_STATUS, null=True, blank=True)
    final_interview_status = models.CharField(max_length=255, choices=FINAL_INTERVIEW_STATUS, null=True, blank=True)
    candidate_initial_info = models.ForeignKey(CandidateInitialInformation, on_delete=models.SET_NULL, null=True, blank=True, related_name='candidates')
    job = models.ManyToManyField("jobs.Job", related_name='candidates')
    interview_schedule = models.ForeignKey("jobs.InterviewSchedule", on_delete = models.CASCADE, null=True, blank=True)
    final_interview = models.ForeignKey("jobs.FinalInterviewSchedule", on_delete=models.CASCADE, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if self.mobile and self.mobile != "Not Found":
            try:
                parsed_mobile = phonenumbers.parse(self.mobile, "BD")
                if phonenumbers.is_valid_number(parsed_mobile):  # Check if the number is valid
                    formatted_mobile = phonenumbers.format_number(parsed_mobile, phonenumbers.PhoneNumberFormat.E164)
                    self.mobile = formatted_mobile
                else:
                    raise ValidationError("Invalid phone number provided.")
            except phonenumbers.phonenumberutil.NumberParseException:
                raise ValidationError("Failed to parse phone number. Ensure it is in a valid format.")
        elif self.mobile == "Not Found":
            self.mobile = "Not Found"  # Optionally clear the field or keep as is
        super().save(*args, **kwargs)
        
    
    def __str__(self):
        return f"{self.name}, {self.mobile}, {self.email}"
    
    
class ContactInfo(models.Model):
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
    religion = models.CharField(max_length=20, blank=True)
    nid = models.CharField(max_length=20, blank=True)
    marital_status = models.CharField(max_length=10, blank=True)

    class Meta:
        abstract = True

class Education(models.Model):
    highest_degree = models.CharField(max_length=100, blank=True)
    degree_name = models.CharField(max_length=100, blank=True)
    subject_highest_degree = models.CharField(max_length=100, blank=True)
    institution_highest_degree = models.CharField(max_length=100, blank=True)
    passing_year_highest_degree = models.CharField(max_length=100, null=True, blank=True)
    division_or_gpa_highest_degree = models.CharField(max_length=100, blank=True)
    professional_degree = models.CharField(max_length=255, null=True, blank=True)
    subject_professional_degree = models.CharField(max_length=255, null=True, blank=True)
    institution_professional_degree = models.CharField(max_length=100, null=True, blank=True)
    passing_year_professional_degree = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        abstract = True
        
class Experience(models.Model):
    current_designation = models.CharField(max_length=100, blank=True)
    current_organization = models.CharField(max_length=100, blank=True)
    total_experience = models.CharField(max_length=100, blank=True)

    class Meta:
        abstract = True


class CandidatesDetails(PersonalInfo,Experience, ContactInfo, Education):
    candidate = models.OneToOneField(Candidate, on_delete=models.CASCADE, related_name='details')

    class Meta:
        verbose_name = 'Candidate Details'
        verbose_name_plural = 'Candidate Details'
        
    def __str__(self):
        return f"Candidate Details for {self.candidate.name}"
    
class Offer(models.Model):
    
    OFFER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    offer_date = models.DateTimeField(auto_now_add=True)
    offered_designation = models.CharField(max_length=100, null=True, blank=True)
    joining_date = models.DateField()
    offer_status = models.CharField(max_length=255, choices=OFFER_STATUS_CHOICES)
    remarks = models.TextField(max_length=255, null=True, blank=True )
    candidate = models.OneToOneField(Candidate, on_delete=models.CASCADE, related_name='offer')
    job = models.ForeignKey("jobs.Job", on_delete=models.CASCADE, related_name='offers',null=True, blank=True)    
    reference_number = models.IntegerField(null=True, blank=True)
    
    
    def save(self, *args, **kwargs):
        if not self.offer_date:
            self.offer_date = timezone.now()
        if not self.reference_number:
            current_month = self.offer_date.month
            current_year = self.offer_date.year
            unit = self.job.unit

            max_reference_number = Offer.objects.filter(
                offer_date__month=current_month,
                offer_date__year=current_year,
                job__unit=unit
            ).aggregate(models.Max('reference_number'))['reference_number__max']

            self.reference_number = (max_reference_number or 0) + 1

        super().save(*args, **kwargs)
        
        job = self.job
        if job:
            accepted_offers_count = Offer.objects.filter(job=job, offer_status='accepted').count()
            job.open_status = accepted_offers_count < job.no_of_position
            if accepted_offers_count >= job.no_of_position:
                job.closing_date = self.joining_date
            else:
                job.closing_date = None
            job.save()

            
    def delete(self, *args, **kwargs):
        job = self.job
        super().delete(*args, **kwargs)
        if job:
            accepted_offers_count = Offer.objects.filter(job=job, offer_status='accepted').count()
            job.open_status = accepted_offers_count < job.no_of_position
            if accepted_offers_count < job.no_of_position:
                job.closing_date = None
            job.save()
            
    def __str__(self):
        return f"Job Offer for {self.candidate.name} for {self.offered_designation}"



class SpreadSheetTracker(models.Model):
    sheet_id = models.CharField(max_length=255, unique=True)
    last_row = models.PositiveBigIntegerField(default=1)

    def __str__(self):
        return self.sheet_id

auditlog.register(Candidate)
auditlog.register(CandidatesDetails)
auditlog.register(Offer)
auditlog.register(CandidateInitialInformation)
auditlog.register(SpreadSheetTracker)