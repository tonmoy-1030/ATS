from django.urls import path
from .views import (job_report, job_report_document, Attendance_sheet,
                    generate_candidate_assessment, offer_letter_generator, 
                    OfferedCandidate, joining_form_generator, employee_list,
                    confirm_appraisal_form, employee_confirmation_list, 
                    generate_confirmation_letter, employee_confirmation_letter_list, generate_transfer_letter,
                    transfer_letter_list,posting_letter_list, generate_posting_letter,
                    appointment_letter_list, generate_appointment_letter, employee_list_envelope, envelopePrinting)

app_name = 'documents'

urlpatterns = [
    path('job-report/<int:job_id>/', job_report, name='job_report'),
    path('job_report_document/<int:job_id>/', job_report_document, name='download_word'),
    path('interview_attendance/<int:interview_id>/', Attendance_sheet, name='interview_attendance'),
    path('interview/<int:interview_id>/assessment/', generate_candidate_assessment, name='interview_assessment'),
    path('candidate/offer-letter/', OfferedCandidate.as_view(), name='offer-letter'),
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
    path('employees/envelope-list/print/', envelopePrinting, name='envelope_print'),

]

