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


# app/admin.py (or any admin.py in your project)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html

class CustomUserAdmin(UserAdmin):
    # Define the columns to display in the user list
    list_display = (
        'username', 
        'email', 
        'first_name', 
        'last_name', 
        'is_staff', 
        'last_login',  # Custom formatted last login
        'date_joined'   
    )


# Unregister the default User admin and register the custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)