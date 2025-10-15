from . import views
from django.urls import path

app_name = 'report'

urlpatterns = [
    path('report/interview_schedule/', views.interviewSchedule, name='Schedule'),
    path('documents/bond/', views.employee_list_bond, name='bond_list'),
    path('documents/bond/paper', views.BondPaper, name='bond_paper'),
    path('report/daily_joining/', views.DailyJoiningCreateView.as_view(), name='daily_joining'),
    path('report/daily_joining/<int:pk>/update/', views.DailyJoiningUpdateView.as_view(), name='daily_joining_update'),
    path('report/daily_joining/<int:pk>/delete/', views.DailyJoiningDeleteView.as_view(), name='daily_joining_delete'),
    path('report/daily_joining/list/', views.DailyJoiningListView.as_view(), name='daily_joining_list'),
    path('report/daily_joining/report/', views.get_daily_joinings, name='daily_joining_report'),
    path('report/daily_joinings/chart/', views.daily_joinings_chart, name='daily_joining_chart'),
    path('report/employee_list/download', views.EmployeeListReport, name='employee_list'),
    path('report/employee_list/salary/download', views.EmployeeListReportWithSalary, name='employee_list_salary'),
    path('report/employee_list/upcoming_joining/download', views.UpcomingJoining, name='employee_upcoming_joining'),
]