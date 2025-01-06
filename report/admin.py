from django.contrib import admin
from .models import DailyJoining
# Register your models here.

@admin.register(DailyJoining)
class DailyJoiningAdmin(admin.ModelAdmin):
    list_display = ('unit', 'date', 'location', 'recruitment_type', 'joinings_count')
    list_filter = ('unit', 'location', 'recruitment_type', 'date')
    search_fields = ('unit__name',)