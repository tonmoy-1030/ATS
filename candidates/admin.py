from django.contrib import admin
from .models import Candidate, Offer, CandidatesDetails, CandidateInitialInformation, SpreadSheetTracker

# Register your models here.
admin.site.register(Offer)
    
@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'mobile', 'email', 'filename', 'initial_interview_status', 'initial_interview_status')
    search_fields = ('name', 'email', 'mobile')
    list_filter = ('initial_interview_status',  'initial_interview_status')
    
@admin.register(CandidatesDetails)
class CandidatesDetailsAdmin(admin.ModelAdmin):
    list_display = ('candidate_name', 'candidate_mobile')
    search_fields = ('candidate_name', 'candidate_mobile')
    
    @admin.display(ordering='candidate__name', description='Candidate Name')
    def candidate_name(self, obj):
        return obj.candidate.name

    @admin.display(ordering='candidate__mobile', description='Candidate Mobile')
    def candidate_mobile(self, obj):
        return obj.candidate.mobile

@admin.register(CandidateInitialInformation)
class CandidateInitialInformationAdmin(admin.ModelAdmin):
    list_display = ('name', 'mobile_no', 'email', 'highest_education_degree', 'display_jobs')
    search_fields = ('name', 'mobile_no')

    
    @admin.display(description="Jobs Applied")
    def display_jobs(self, obj):
        return obj.jobs.first().job_title
    
@admin.register(SpreadSheetTracker)
class SpreadSheetTrackerAdmin(admin.ModelAdmin):
    list_display = ('sheet_id', 'last_row')
    search_fields = ('sheet_id',)