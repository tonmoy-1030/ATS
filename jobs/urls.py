from django.urls import path
from . import views
from django.contrib.auth import views as auth_view
from .views import (JobDetailView,
                    JobUpdateView, 
                    ScheduleDetailview,
                    FinalScheduleDetailview,
                    HeadcountCreateview,
                    HeadCountListView,
                    ShortListedCandidate,
                    home,
                    InitialInterviewList,
                    FinalInitialInterviewList, 
                    ScheduleUpdateView, 
                    FinalScheduleUpdateView
                    )
app_name = 'jobs'

urlpatterns = [
    path('', home.as_view(), name='home'),
    path('accounts/login/', auth_view.LoginView.as_view(template_name='jobs/login.html'), name='login'),    
    path('logout/', auth_view.LogoutView.as_view(template_name='jobs/logout.html'), name='logout'),
    path('headcount/all', HeadCountListView.as_view(), name='headcount-list'),
    path('headcount/new',HeadcountCreateview.as_view(), name='create-headcount'),
    path('headcount/<int:pk>/',JobDetailView.as_view(), name='job_details'),
    path('headcount/<int:pk>/update/',JobUpdateView.as_view(), name='job_update'),    
    path('initial_interview/',InitialInterviewList.as_view(), name='initial_interview_list'),
    path('final_interview/',FinalInitialInterviewList.as_view(), name='final_interview_list'),
    path('interview/<int:pk>/', ScheduleDetailview.as_view(), name='interview_details'),
    path('final/<int:pk>/', FinalScheduleDetailview.as_view(), name='final_interview_details'),
    path('final/<int:pk>/shortlisted', ShortListedCandidate.as_view(), name='shortlisted'),
    path('final/<int:pk>/finalize_final_interview/', views.finalize_final_interview, name='finalize_final_interview'),
    path('final/<int:pk>/remove_candidate/', views.remove_from_final_interview, name='remove_final_interview_candidate'),
    path('create_schedule/', views.create_schedule, name='create_schedule'),
    path('initial/schedule/<int:pk>', ScheduleUpdateView.as_view(), name='update_schedule'),
    path('final/schedule/<int:pk>', FinalScheduleUpdateView.as_view(), name='update_final_schedule'),
    path('ajax/load-jobs/', views.load_jobs, name='ajax_load_jobs'),
    path('job/expend/vacancy', views.expands_requisition.as_view(), name='expend_requisition'),
    path('job/expend/joining', views.expands_joining_list.as_view(), name='expend_joining'),
    

]   