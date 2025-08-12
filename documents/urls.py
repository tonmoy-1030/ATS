from django.urls import path
from . import views
from .views import (job_report, job_report_document, Attendance_sheet,
                    generate_candidate_assessment, offer_letter_generator, 
                    JobOfferList, joining_form_generator, employee_list,
                    confirm_appraisal_form, employee_confirmation_list, 
                    generate_confirmation_letter, employee_confirmation_letter_list, generate_transfer_letter,
                    transfer_letter_list,posting_letter_list, generate_posting_letter,
                    appointment_letter_list, generate_appointment_letter, employee_list_envelope, envelopePrinting,
                    candidateReport, employeeList)

app_name = 'documents'

urlpatterns = [
    path('job-report/<int:job_id>/', job_report, name='job_report'),
    path('job_report_document/<int:job_id>/', job_report_document, name='download_word'),
    path('interview_attendance/<int:interview_id>/', Attendance_sheet, name='interview_attendance'),
    path('interview/<int:interview_id>/assessment/', generate_candidate_assessment, name='interview_assessment'),
    path('candidate/offer-letter/', JobOfferList, name='offer-letter'),
    path('candidate/offer-print/', offer_letter_generator, name='offer-print'),
    path('employee/joining-form/', joining_form_generator, name='joining-form'),
    path('employees/joining-form-list/', employee_list, name='joining-form-list'),
    path('employee/confirm_appraisal_document/', confirm_appraisal_form, name='confirm_document'),
    path('employee/confirm_employee_list/', employee_confirmation_list, name='employee_confirmation_list'),
    path('employee/confirm_employee_letter_list/', employee_confirmation_letter_list, name='employee_confirmation_letter_list'),
    path('employees/confirmation_letter', generate_confirmation_letter, name = 'confirmation_letter'),
    path('employees/transfer_letter', generate_transfer_letter, name = 'transfer_letter'), #Generating Letter
    path('employees/posting_letter', generate_posting_letter, name = 'posting_letter'), #Generating Letter
    path('employee/transfer_order_list/', transfer_letter_list, name='transfer_order_list'),
    path('employee/posting_order_list/', posting_letter_list, name='posting_order_list'),
    path('employee/appointment_list/', appointment_letter_list, name='appointment_letter_list'),
    path('employee/appointment_letter/', generate_appointment_letter, name='appointment_letter'),
    path('employees/envelope-list/', employee_list_envelope, name='envelope_list'),
    path('employees/envelope-print/', envelopePrinting, name='envelope_print'),
    path('employees/name-tag-list/', views.employee_list_name_tag, name='name_tag_list'),
    path('employees/name-tag-list/print/', views.nameTagPrinting, name='name_tag_print'),
    path('report/Candidate_report/', candidateReport, name='Candidate_report'),
    path('report/employee_list/', employeeList, name='employee_download'),
    path('export/jobs/pdf/', views.generate_jobs_pdf, name='export_jobs_pdf'),
    path('report/interview_summary/<int:final_interview_id>/', views.Interview_Summary, name='interview_summary'),

]

