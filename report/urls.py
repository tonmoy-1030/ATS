from . import views
from django.urls import path

app_name = 'report'

urlpatterns = [
    path('report/interview_schedule/', views.interviewSchedule, name='Schedule'),
    
]