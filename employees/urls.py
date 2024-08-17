from django.urls import path
from .views import (
                    EmployeeListView, EmployeeCreateView,
                    upload_file, sample_employee_upload_file, 
                    EmployeeSeparationCreateView, get_candidate_data,
                    EmployeeUpdateView, 
                    employee_details,
                    EmployeeSeperationUpdateView,
                    employee_confirmation,
                    employee_search, transfer_order, posting_order,
                    separate_upload_file,
                    EmployeeProfile,
                    EmployeeSalaryInfo
                
                    )

app_name = 'employees'

urlpatterns = [
    path('employees/', EmployeeListView.as_view(), name='employee'),
    path('employee/profile/<int:pk>', EmployeeProfile.as_view(), name='employee_profile' ),
    path('employee/upload/csv',upload_file , name='import_employee_csv' ),
    path('employees/create', EmployeeCreateView.as_view(), name='employee-create'),
    path('employees/sample', sample_employee_upload_file, name='sample_employee'),
    path('employees/seperation', EmployeeSeparationCreateView.as_view(), name='employee-seperation'),
    path('seperation/update/<int:id>', EmployeeSeperationUpdateView.as_view(), name='seperation-update'),
    path('employees/update/<int:pk>', EmployeeUpdateView.as_view(), name='employee-update'),
    path('get_candidate_data/', get_candidate_data, name='get_candidate_data'),
    path('employee_details/', employee_details, name='emp-details'),
    path('employees/confirmation', employee_confirmation, name = 'employee-confirmation'),
    path('employees/search', employee_search),
    path('employee/transfer_order', transfer_order, name='employee-transfer'),
    path('employee/posting_order', posting_order, name='employee-posting'),
    path('seperate/upload/csv',separate_upload_file , name='seperate_csv' ),
    path('employee/salary',EmployeeSalaryInfo.as_view() , name='salary_info' ),
]