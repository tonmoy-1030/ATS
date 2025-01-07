from django.db import models
from django.utils import timezone
from jobs.models import BusinessUnit
from django.contrib.auth.models import User
from auditlog.registry import auditlog


class DailyJoining(models.Model):
    
    RECRUITMENT_CHOICES = [
        ('Replace', 'Replacement'),
        ('New Position', 'New Position'),
    ]
    
    EMPLOYMENT_TYPE_CHOICES = [
        ("Permanent", "Permanent"), 
        ("Contractual", "Contractual")
        ]
    
    timestamp = models.DateTimeField(default=timezone.now)
    unit = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE, related_name="joinings")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date = models.DateField()
    location = models.CharField(max_length=20)
    employee_category = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES)
    recruitment_type = models.CharField(max_length=20, choices=RECRUITMENT_CHOICES)
    joinings_count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Daily Joining"
        verbose_name_plural = "Daily Joinings"
        ordering = ['date', 'unit']

    def __str__(self):
        return f"{self.unit} ({self.location}, {self.recruitment_type}) - {self.date}: {self.joinings_count} joinings"

auditlog.register(DailyJoining)