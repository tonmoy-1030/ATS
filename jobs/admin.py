from django.contrib import admin
from .models import Job, InterviewSchedule, FinalInterviewSchedule, BusinessUnit

admin.site.register(InterviewSchedule)
admin.site.register(FinalInterviewSchedule)
admin.site.register(BusinessUnit)


class JobAdmin(admin.ModelAdmin):
    list_display = ('job_title', 'department', 'unit', 'job_location', 'posting_date', 'types', 'no_of_position', 'closing_date', 'open_status')
    list_filter = ('department', 'unit', 'posting_date', 'types', 'open_status')
    search_fields = ('job_title', 'department', 'unit__name', 'job_location')
    list_per_page = 20

    
admin.site.register(Job, JobAdmin)