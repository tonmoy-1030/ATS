from django.contrib import admin
from .models import Job, InterviewSchedule, FinalInterviewSchedule

admin.site.register(Job)
admin.site.register(InterviewSchedule)
admin.site.register(FinalInterviewSchedule)