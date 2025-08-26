from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
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
                    EmployeeSalaryInfo, EmployeeDeleteView, 
                    unit_based_employee_search
                
                    )
from . import views

app_name = 'employees'

urlpatterns = [
    path('employees/', EmployeeListView.as_view(), name='employee'),
    path('employee/profile/<int:pk>', EmployeeProfile.as_view(), name='employee_profile' ),
    path('employee/upload/csv',upload_file , name='import_employee_csv' ),
    path('employees/create', EmployeeCreateView.as_view(), name='employee-create'),
    path('employees/<int:pk>/delete', EmployeeDeleteView.as_view(), name='employee-delete'),
    path('employees/sample', sample_employee_upload_file, name='sample_employee'),
    path('employees/separation', EmployeeSeparationCreateView.as_view(), name='employee-seperation'),
    path('separation/update/<int:id>', EmployeeSeperationUpdateView.as_view(), name='seperation-update'),
    path('employees/update/<int:pk>', EmployeeUpdateView.as_view(), name='employee-update'),
    path('get_candidate_data/', get_candidate_data, name='get_candidate_data'),
    path('employee_details/', employee_details, name='emp-details'),
    path('employees/confirmation', employee_confirmation, name = 'employee-confirmation'),
    path('employees/search', employee_search),
    path('employee/transfer_order', transfer_order, name='employee-transfer'),
    path('employee/posting_order', posting_order, name='employee-posting'),
    path('separate/upload/csv',separate_upload_file , name='import_separate_csv' ),
    path('employee/salary',EmployeeSalaryInfo.as_view() , name='salary_info' ),
    path('employees/unit/search', unit_based_employee_search),
    path('transfer/update/<int:pk>', views.TransferUpdateView.as_view(), name='transfer-update'),
    path('posting/update/<int:pk>', views.PostingUpdateView.as_view(), name='posting-update'),
    path('employees/separation/list', views.EmployeeSeparationListView.as_view(), name='employee-separation'),
    path('employees/separation/sample', views.sample_separated_upload_file, name='sample_separation'),
    path('employees/documents', views.OfficialDocumentCreateView.as_view(), name='employee_documents'),
    path('employees/documents/<int:pk>/update', views.OfficialDocumentUpdateView.as_view(), name='employee_document_update'),
    path('employees/documents/<int:pk>/delete', views.OfficialDocumentDeleteView.as_view(), name='employee_document_delete'),
    path('employee/sales_officer/google_sheet', views.Sales_Officer_Google_Sheet, name='sales_officer_google_sheet'),
    path('employee/sales_officer/create', views.SalesOfficerCreateView.as_view(), name='sales_officer_create')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)