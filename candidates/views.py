from django.db.models.query import QuerySet
from django.http import  HttpResponse, HttpResponseNotFound, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .utls.data_extraction import DataExtraction
from .utls.text_converter import TextConverter
from .utls.data import DataFromCV
from .forms import (FileFieldForm,  InitialCandidateUpdateForm ,
                    FinalCandidateUpdateForm,JobOfferForm, JobOfferCreateForm,
                    JobOfferFilter)  
from django.views.generic import (FormView, 
                                  UpdateView, 
                                  DeleteView, 
                                  CreateView, 
                                  ListView, 
                                  DetailView
                                  )

import google.generativeai as genai
import os
from django.db.models import Count, Q
from django.contrib.messages.views import SuccessMessageMixin
from django.conf import settings  
from .models import Candidate, Offer, CandidatesDetails
from jobs.models import InterviewSchedule, Job, FinalInterviewSchedule
from django.forms import modelformset_factory
from .utls.google_form_Candidates import process_responses, get_authenticated_service, get_form_responses
import csv
from django.contrib import messages
import logging
import time
from requests.exceptions import RequestException


from employees.models import Employee
from .utls.google_sheet_Candidates import candidateDate
from datetime import datetime        
import json 
logger = logging.getLogger(__name__)


TextConverter = TextConverter()
DataExtraction = DataExtraction()

def Resume_Date_As_JSON(prompts):
  genai.configure(api_key="AIzaSyB_WKoQ8d27_Zo9lNhOpH3zdRuf0XJ1EEc")
  model = genai.GenerativeModel(
  model_name="gemini-2.0-flash-lite",
  generation_config={"response_mime_type": "application/json",}
  )
  chat_session = model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [
                        prompts,
                        """
                        Think you are an ATS system. Extract from the text in json format and keep the keys in the same format as below even if there is not data: 
                        {
                        "Name": "",
                        "Phone": "",
                        "Email": "",
                        "Highest_Educational_Degree": "",
                        "Passing_Year": "",
                        "Highest_Education_Degree_Institution": "",
                        "Professional_Degree": "",
                        "Experience": [
                            {
                            "Position": "",
                            "Company": "",
                            "Duration": ""
                            }
                        ],
                        "Permanent_Address": ""
                        }
                        
                        do not give list format. provide the output in json format only.
                        """,
                    ],
                }
            ]
        )
  response = chat_session.send_message("Extract the requested details.")
  json_response = json.loads(response.text)
  return json_response


def ResumeExtractor(file):
    temp_directory = os.path.join(settings.MEDIA_ROOT, 'temp')
    os.makedirs(temp_directory, exist_ok=True)

    temp_file_path = os.path.join(temp_directory, file.name)
    with open(temp_file_path, 'wb') as temp_file:
        for chunk in file.chunks():
            temp_file.write(chunk)
    try:
        if temp_file_path.endswith(".pdf"):
            extracted_textinfo = TextConverter.pdf_to_text(temp_file_path)
        elif temp_file_path.endswith(".doc"):
            extracted_textinfo = TextConverter.doc_to_text(temp_file_path)
        elif temp_file_path.endswith(".docx"):
            extracted_textinfo = TextConverter.docx_to_text(temp_file_path)
        elif temp_file_path.endswith(".jpg") or temp_file_path.endswith(".jpeg") or temp_file_path.endswith(".png"):
            extracted_textinfo = TextConverter.img_to_text(temp_file_path)
        else:
            raise ValueError("Unsupported file format")
    except Exception as e:
        logging.error(f"Error extracting text from file: {e}")
        raise
    os.remove(temp_file_path)
    response = None
    try:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = Resume_Date_As_JSON("\n".join(extracted_textinfo))
                if response:
                    break
            except RequestException as e:
                logging.error(f"Network error on attempt {attempt + 1}: {e}")
                time.sleep(2 ** attempt)  
            except Exception as e:
                logging.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                break

        if response:
            try:
                name = response['Name'].title()
            except Exception as e:
                logging.error(f"Error processing response: {e}")
                name = DataExtraction.extract_name(extracted_textinfo)
        else:
            name = DataExtraction.extract_name(extracted_textinfo)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        name = DataExtraction.extract_name(extracted_textinfo)


    data = DataFromCV(file_name=DataExtraction.extract_file_name(file),
                      name=name,
                      phone=DataExtraction.extract_phonenumbers(extracted_textinfo),
                      email=DataExtraction.extract_emails(extracted_textinfo))
    return data
  
  


class FileFieldFormView(FormView):
    form_class = FileFieldForm
    template_name = "candidates/upload.html"

    def form_valid(self, form):
        files = form.cleaned_data["file_field"]
        interview_schedule_pk = self.kwargs.get('pk')
        interview_schedule = get_object_or_404(InterviewSchedule, pk=interview_schedule_pk)
        jobs = interview_schedule.job.all()

        total_files = len(files)
        session_key = f'upload_progress_{interview_schedule_pk}'
        self.request.session[session_key] = 0  # Initialize progress to 0
        self.request.session.modified = True
        self.request.session.save()

        try:
            for i, file in enumerate(files, 1):
                try:
                    # Extract resume info (replace ResumeExtractor with your actual logic)
                    resume_info = ResumeExtractor(file)
                    candidate = Candidate(
                        name=resume_info.name,
                        mobile=resume_info.phone,
                        email=resume_info.email,
                        filename=resume_info.file_name,
                        attendance_status='absent',
                        interview_schedule=interview_schedule
                    )
                    candidate.save()
                    candidate.job.set(jobs)

                except Exception as e:
                    # Log the error and continue processing other files
                    logger.error(f"Error processing file {file.name}: {e}")
                    continue

                # Calculate and update progress
                progress = int((i / total_files) * 100)
                self.request.session[session_key] = progress
                self.request.session.modified = True
                self.request.session.save()

            # Ensure final progress is set to 100 when all files are uploaded
            self.request.session[session_key] = 100
            self.request.session.modified = True
            self.request.session.save()

            return JsonResponse({'status': 'success'})

        except Exception as e:
            logger.error(f"Unexpected error during file processing: {e}")
            self.request.session[session_key] = -1  # Indicate failure
            self.request.session.modified = True
            self.request.session.save()
            return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred. Please try again later.'}, status=500)

    def form_invalid(self, form):
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)



# Helper view to return progress
def get_upload_progress(request, pk):
    session_key = f'upload_progress_{pk}'
    progress = request.session.get(session_key, 0)  # Default to 0 if progress is not found
    return JsonResponse({'progress': progress})

class final_FileFieldFormView(FormView):
    form_class = FileFieldForm
    template_name = "candidates/upload.html"

    def form_valid(self, form):
        files = form.cleaned_data["file_field"]
        interview_schedule_pk = self.kwargs.get('pk')
        interview_schedule = get_object_or_404(FinalInterviewSchedule, pk=interview_schedule_pk)
        jobs = interview_schedule.job.all()

        for file in files:
            resume_info = ResumeExtractor(file)
            candidate = Candidate(name=resume_info.name, mobile=resume_info.phone,
                                  email=resume_info.email, filename=resume_info.file_name,
                                  attendance_status='absent', final_interview=interview_schedule)
            candidate.save()
            candidate.job.set(jobs)

    
        self.interview_schedule_pk = interview_schedule_pk
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('jobs:final_interview_details', kwargs={'pk': self.interview_schedule_pk})
    
    
#many to many relationship    
class CandidateCreateView(SuccessMessageMixin, CreateView):
    model = Candidate
    fields = ['name','email','mobile']
    
    def form_valid(self, form):
        interview_schedule_pk = self.kwargs.get('pk')
        interview_schedule = get_object_or_404(InterviewSchedule, pk=interview_schedule_pk)
        jobs = interview_schedule.job.all()
        
        form.instance.interview_schedule = interview_schedule
        Candidate = form.save()
        
        Candidate.job.set(jobs)
        
        self.interview_schedule_pk = interview_schedule_pk
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('jobs:interview_details', kwargs={'pk': self.interview_schedule_pk})
    
    success_message = '%(name)s is entered successfully'
    
#end here

class CandidateUpdateView(UpdateView):
    model = Candidate
    
    fields = ['name','email','mobile','invitation_status', 'attendance_status', 'initial_interview_status']

    def get_success_url(self):
        interview_schedule = self.object.interview_schedule
        interview_schedule_pk = interview_schedule.pk
        return reverse('jobs:interview_details', kwargs={'pk': interview_schedule_pk})
    
class FinalCandidateUpdateView(UpdateView):
    model = Candidate
    
    fields = ['name','email','mobile', 'final_interview_attendance', 'final_interview_status']

    def get_success_url(self):
        interview_schedule = self.object.final_interview
        interview_schedule_pk = interview_schedule.pk
        return reverse('jobs:final_interview_details', kwargs={'pk': interview_schedule_pk})
    
def initial_update_candidates(request, pk):
    interview_schedule = get_object_or_404(InterviewSchedule, pk=pk)
    CandidateFormSet = modelformset_factory(
        Candidate,
        form=InitialCandidateUpdateForm,
        extra=0
    )    

    if request.method == 'POST':
        formset = CandidateFormSet(request.POST, queryset=Candidate.objects.filter(interview_schedule=interview_schedule))
        if formset.is_valid():
            formset.save()
            return redirect('jobs:interview_details', pk=pk)
    else:
        formset = CandidateFormSet(queryset=Candidate.objects.filter(interview_schedule=interview_schedule))

    return render(request, 'candidates/update_candidates.html', {'formset': formset})


def Final_update_candidates(request, pk):
    final_interview = get_object_or_404(FinalInterviewSchedule, pk=pk)
    CandidateFormSet = modelformset_factory(
        Candidate,
        form=FinalCandidateUpdateForm,
        extra=0
    )    
    if request.method == 'POST':
        formset = CandidateFormSet(request.POST, queryset=Candidate.objects.filter(final_interview=final_interview))
        if formset.is_valid():
            formset.save()
            return redirect('jobs:final_interview_details', pk=pk)
    else:
        formset = CandidateFormSet(queryset=Candidate.objects.filter(final_interview=final_interview))

    return render(request, 'candidates/Final_update_candidates.html', {'formset': formset})


    
class CandidateDeleteView(DeleteView):
    model = Candidate

    def get_success_url(self):
        interview_schedule = self.object.interview_schedule
        interview_schedule_pk = interview_schedule.pk
        return reverse('jobs:interview_details', kwargs={'pk': interview_schedule_pk})
    
#################################
    
class CandidateListView(ListView):
    model = Candidate
    template_name = "candidates/candidate_list.html"
    context_object_name = 'candidates'
    paginate_by = 13

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')

        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(mobile__icontains=query) |
                Q(email__icontains=query)
            )
        elif query == '':
            queryset = Candidate.objects.all()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_candidates = Candidate.objects.all()
        duplicate_mobiles = all_candidates.values('mobile').annotate(count=Count('mobile')).filter(count__gt=1).values_list('mobile', flat=True)

        context['duplicate_mobiles'] = duplicate_mobiles
        return context
    
    
class CandidateDetailView(DetailView):
    model = Candidate
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        candidate = get_object_or_404(Candidate, pk=self.kwargs['pk'])
        candidates = Candidate.objects.filter(mobile=candidate.mobile)
        context['candidate_occurance'] = candidates
        return context


class JobOfferCreateView(CreateView):
    model = Offer
    form_class = JobOfferCreateForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        candidate_id = self.kwargs['pk']
        candidate = Candidate.objects.get(pk=candidate_id)
        existing_offer = Offer.objects.filter(candidate=candidate).first()
        context['candidate'] = candidate
        context['offer_exists'] = existing_offer
        return context

    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['candidate_id'] = self.kwargs['pk']
        return kwargs

    
    def form_valid(self, form):
        candidate_id = self.kwargs['pk']
        form.instance.candidate_id = candidate_id
        self.object = form.save()
        return redirect(self.get_success_url())

    
    def get_success_url(self):
        return reverse('jobs:final_interview_details', kwargs={'pk': self.object.candidate.final_interview.id})
  
class JobOfferUpdateView(UpdateView):
    model = Offer
    form_class = JobOfferForm
    template_name = 'candidates/offer-update.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        offer = Offer.objects.get(id=self.kwargs['pk'])
        kwargs['candidate_id'] = offer.candidate.id
        return kwargs

    
    def form_valid(self, form):
        offer = Offer.objects.get(id=self.kwargs['pk'])
        form.instance.candidate_id = offer.candidate.id
        self.object = form.save()
        return redirect(self.get_success_url())
    
    def get_success_url(self):
        # Try to get 'next' parameter from the GET request
        next_url = self.request.GET.get('next')
        # If 'next' exists, redirect to it, otherwise redirect to a default fallback
        if next_url:
            return next_url
        return reverse('default_fallback')
   
class OfferDeleteview(DeleteView):
    model = Offer

    def get_success_url(self):
        return reverse('jobs:final_interview_details', kwargs={'pk': self.object.candidate.final_interview.id})

class OfferListView(ListView):
    model = Offer
    template_name = 'candidates/offer-list.html'
    context_object_name = 'offers'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = super().get_queryset()    
        self.filterset = JobOfferFilter(self.request.GET, queryset=queryset.order_by('-offer_date').distinct())
        return self.filterset.qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
          # Create a dictionary to check if the candidate is an employee
        offer_is_employee = {
            offer.id: Employee.objects.filter(candidate=offer.candidate).exists()
            for offer in self.filterset.qs
        }
        
        # Collect only the IDs where the candidate is an employee
        employee_offer_ids = [offer_id for offer_id, is_employee in offer_is_employee.items() if is_employee]
        
        context['employee_offer_ids'] = employee_offer_ids
        return context

def CandidateDetailsUpdate(request):
    # Define field IDs or keys from your Google Form responses
    FIELD_IDS = {
        'name': 'Name',
        'BLOOD_GROUP': 'Blood Group',
        'DOB': 'Date of Birth',
        'MARITIAL_STATUS': 'Marital Status',
        'CURRENT_DESIGNATION': 'Current Designation',
        'CURRENT_ORGANIZATION': 'Current Organization',
        'TOTAL_EXPERIENCE': 'Total Experience',
        'PRESENT_VILL': 'Present Vill',
        'PRESENT_PO': 'Present Post office',
        'PRESENT_PS': 'Present Police Station',
        'PRESENT_DISTRICT': 'Present District',
        'PERMANENT_VILL': 'Permanent Vill',
        'PERMANENT_PO': 'Permanent Post Office',
        'PERMANENT_PS': 'Permanent Police Station',
        'PERMANENT_DISTRICT': 'Permanent District',
        'HIGHEST_DEGREE': 'Highest Degree',
        'DEGREE_NAME': 'Degree Name',
        'SUBJECT': 'Subject_',
        'PASSING_YEAR': 'Passing Year_',
        'INISTITUTION': 'Institution_',
        'CGPA': 'Division/GPA',
        'ANY_PROFESSIONAL_DEGREE': 'Do you have any Professional Degree?',
        'PROFESSIONAL_DEGREE': 'Professional Degree',
        'PROFESSIONAL_SUBJECT': "Professional Degree's Subject",
        'PROFESSIONAL_INISTITUTION': "Professional Degree's Institution",
        'PROFESSIONAL_PASSING_YEAR': "Professional Degree's  Passing Year",
        'NID': 'NID No.',
        'religion': 'Religion',
        'email': 'Email',
        'inputted_others':'Enter Your University Name'
    }

    alert_messages = []
    candidate_data = candidateDate()  # Fetch data from Google Sheet
    if candidate_data:

        for mobile, details in candidate_data.items():
            try:
                candidate = Candidate.objects.filter(mobile=mobile).last()

                if candidate:
                    if not hasattr(candidate, 'details'):
                        CandidatesDetails.objects.create(candidate=candidate)

                    # Parse Date of Birth with the correct format (MM/DD/YYYY)
                    dob_str = details.get(FIELD_IDS['DOB'], "")
                    if dob_str:
                        try:
                            # Assuming the date format is MM/DD/YYYY
                            dob = datetime.strptime(dob_str, "%m/%d/%Y").date()
                        except ValueError:
                            alert_messages.append(f"Invalid date format for {mobile}: {dob_str}")
                            continue
                    else:
                        dob = None

                    # Update CandidateDetails object with form responses
                    details_obj = candidate.details
                    candidate.email = details.get(FIELD_IDS['email'], "")
                    details_obj.present_vill = details.get(FIELD_IDS['PRESENT_VILL'], "")
                    details_obj.present_po = details.get(FIELD_IDS['PRESENT_PO'], "")
                    details_obj.present_ps = details.get(FIELD_IDS['PRESENT_PS'], "")
                    details_obj.present_dist = details.get(FIELD_IDS['PRESENT_DISTRICT'], "")
                    details_obj.permanent_vill = details.get(FIELD_IDS['PERMANENT_VILL'], "")
                    details_obj.permanent_po = details.get(FIELD_IDS['PERMANENT_PO'], "")
                    details_obj.permanent_ps = details.get(FIELD_IDS['PERMANENT_PS'], "")
                    details_obj.permanent_dist = details.get(FIELD_IDS['PERMANENT_DISTRICT'], "")
                    details_obj.date_of_birth = dob
                    details_obj.blood_group = details.get(FIELD_IDS['BLOOD_GROUP'], "")
                    details_obj.marital_status = details.get(FIELD_IDS['MARITIAL_STATUS'], "")
                    details_obj.current_designation = details.get(FIELD_IDS['CURRENT_DESIGNATION'], "")
                    details_obj.current_organization = details.get(FIELD_IDS['CURRENT_ORGANIZATION'], "")
                    details_obj.total_experience = details.get(FIELD_IDS['TOTAL_EXPERIENCE'], "")
                    details_obj.highest_degree = details.get(FIELD_IDS['HIGHEST_DEGREE'], "")
                    details_obj.degree_name = details.get(FIELD_IDS['DEGREE_NAME'], "")
                    details_obj.subject_highest_degree = details.get(FIELD_IDS['SUBJECT'], "")
                    details_obj.passing_year_highest_degree = details.get(FIELD_IDS['PASSING_YEAR'], "")
                    if details.get(FIELD_IDS['INISTITUTION'], "") != "Others":
                        details_obj.institution_highest_degree = details.get(FIELD_IDS['INISTITUTION'], "")
                    else:
                         details_obj.institution_highest_degree = details.get(FIELD_IDS['inputted_others'], "")
                    details_obj.division_or_gpa_highest_degree = details.get(FIELD_IDS['CGPA'], "")
                    details_obj.professional_degree = details.get(FIELD_IDS['PROFESSIONAL_DEGREE'], "")
                    details_obj.subject_professional_degree = details.get(FIELD_IDS['PROFESSIONAL_SUBJECT'], "")
                    details_obj.institution_professional_degree = details.get(FIELD_IDS['PROFESSIONAL_INISTITUTION'], "")
                    details_obj.passing_year_professional_degree = details.get(FIELD_IDS['PROFESSIONAL_PASSING_YEAR'], "")
                    details_obj.nid = details.get(FIELD_IDS['NID'], "")
                    details_obj.religion = details.get(FIELD_IDS['religion'], "")
                    details_obj.save()
                    candidate.save()

                else:
                    alert_messages.append(f"Candidate with mobile number {mobile}-{details.get(FIELD_IDS['name'], '')} not found.")
        
            except Candidate.DoesNotExist:
                alert_messages.append(f"Candidate with mobile number {mobile}-{details.get(FIELD_IDS['name'], '')} not found.")
            except Exception as e:
                alert_messages.append(f"Error processing details for {mobile}: {e}")

    else:
        alert_messages.append("No responses found from the form.")

    if not alert_messages:
        alert_messages.append("All Candidate details updated successfully.")

    return JsonResponse({'alert_messages': alert_messages})



class CandidateDetailsListView(ListView):
    template_name = 'candidates/candidate_details_list.html'
    model = Candidate
    context_object_name = 'candidates'
    paginate_by = 15
    
    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')

        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(mobile__icontains=query) |
                Q(email__icontains=query)
            )
        elif query == '':
            queryset = Candidate.objects.all()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_candidates = Candidate.objects.all()
        duplicate_mobiles = all_candidates.values('mobile').annotate(count=Count('mobile')).filter(count__gt=1).values_list('mobile', flat=True)
        context['duplicate_mobiles'] = duplicate_mobiles
        return context

    
def candidate_csv_download(request):
    candidates = Candidate.objects.all()
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="candidate_details.csv"'},
    )   
    
    writer = csv.writer(response)
    header_row = [
        'SL','Name', 'Mobile', 'Email', 'Attendance Status', 'Invitation Status',
        'Initial Interview Status', 'Final Interview Attendance', 'Final Interview Status',
        'Job', 'Unit', 'Date of Birth', 'Blood Group', 'Religion', 'NID', 'Marital Status',
        'Present Village', 'Present Post Office', 'Present Police Station', 'Present District',
        'Permanent Village', 'Permanent Post Office', 'Permanent Police Station', 'Permanent District',
        'Highest Degree', 'Degree Name', 'Subject (Highest Degree)', 'Institution (Highest Degree)', 'Passing Year (Highest Degree)', 'Division or GPA (Highest Degree)',
        'Professional Degree', 'Professional Subject', 'Institution (Professional Degree)', 'Passing Year (Professional Degree)',
        'Current Designation', 'Current Organization', 'Total Experience'
    ]
    writer.writerow(header_row)
    for index, candidate in enumerate(candidates, start=1):
        if hasattr(candidate, 'details'):
            details = candidate.details
        else:
            details = None
        row = [
            index,
            candidate.name,
            candidate.mobile,
            candidate.email,
            candidate.attendance_status,
            candidate.invitation_status,
            candidate.initial_interview_status,
            candidate.final_interview_attendance,
            candidate.final_interview_status,
            candidate.job.first().job_title if candidate.job.exists() else '',
            candidate.job.first().unit if candidate.job.exists() else '',
            details.date_of_birth if details else '',
            details.blood_group if details else '',
            details.religion if details else '',
            details.nid if details else '',
            details.marital_status if details else '',
            details.present_vill if details else '',
            details.present_po if details else '',
            details.present_ps if details else '',
            details.present_dist if details else '',
            details.permanent_vill if details else '',
            details.permanent_po if details else '',
            details.permanent_ps if details else '',
            details.permanent_dist if details else '',
            details.highest_degree if details else '',
            details.degree_name if details else '',
            details.subject_highest_degree if details else '',
            details.institution_highest_degree if details else '',
            details.passing_year_highest_degree if details else '',
            details.division_or_gpa_highest_degree if details else '',
            details.professional_degree if details else '',
            details.subject_professional_degree if details else '',
            details.institution_professional_degree if details else '',
            details.passing_year_professional_degree if details else '',
            details.current_designation if details else '',
            details.current_organization if details else '',
            details.total_experience if details else ''
        ]
        writer.writerow(row)
    return response
