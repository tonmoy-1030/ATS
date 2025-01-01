from . import views
from django.urls import path

app_name = 'report'

urlpatterns = [
    path('report/interview_schedule/', views.interviewSchedule, name='Schedule'),
    path('documents/bond/', views.employee_list_bond, name='bond_list'),
    path('documents/bond/paper', views.BondPaper, name='bond_paper'),
]