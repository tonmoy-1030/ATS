from django.urls import path
from . import views

app_name = 'leave'

urlpatterns = [
    path('leaves/allocation', views.LeaveAllocationCreateView.as_view(), name='leaveAllocation'),
    path('leaves/application', views.LeaveApplicationCreateView.as_view(), name='leaveApplication'),
    path('calculate-leave-days/', views.calculate_leave_days, name='calculate_leave_days'),
    path('leaves/application/list', views.LeaveApplicationList, name='leaveApplication_list'),
    path('leaves/allocation/list', views.LeaveAllocationList, name='leaveAllocation_list'),
    path('leaves/application/update/<int:pk>', views.LeaveApplicationUpdateView.as_view(), name='leaveApplicationUpdate'),
    path('leaves/allocation/update/<int:pk>', views.LeaveAllocationUpdateView.as_view(), name='leaveAllocationUpdate'),   
    path('leaves/holiday', views.HolidayCreateView.as_view(), name="holiday"),
    path('leaves/holiday/update/<int:pk>', views.HolidayUpdateView.as_view(), name="holidayUpdate"),
    path('leaves/holiday/list', views.holidayList, name="holidayList"),
    path('leaves/upload/csv',views.upload_file , name='leave_csv' ),
    path('leaves/allocation/delete/<int:pk>',views.LeaveAllocationDeleteView.as_view() , name='allocationDelete' ),
    path('leaves/application/delete/<int:pk>',views.LeaveApplicationDeleteView.as_view() , name='applicationDelete' ),
    path('leaves/allocation/process',views.leave_allocation_process , name='application_yearly_process' ),
    path('api/run-recalculation/', views.run_leave_recalculation, name='run_recalculation'),
    path('leaves/application/process/page',views.leave_processing_page , name='application_process_page' ),
]   