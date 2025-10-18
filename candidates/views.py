from django.db.models.query import QuerySet
from django.http import  HttpResponse, HttpResponseNotFound, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .utils.data_extraction import DataExtraction
from .utils.text_converter import TextConverter
from .utils.data import DataFromCV
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
from .models import Candidate, Offer, CandidatesDetails, CandidateInitialInformation
from jobs.models import InterviewSchedule, Job, FinalInterviewSchedule
from django.forms import modelformset_factory
from django.contrib import messages
import logging
from django.utils import timezone
from requests.exceptions import RequestException
from .utils.google_sheet_Candidates import CandidateGoogleSheet 
from employees.models import Employee
from datetime import datetime        
import json
from django.db.models import Case, When, Value, IntegerField
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import Case, When, Value, IntegerField
import csv
import tempfile
from decouple import config
 
logger = logging.getLogger(__name__)


TextConverter = TextConverter()
DataExtraction = DataExtraction()
candidate_google_sheet = CandidateGoogleSheet()

def Resume_Date_As_JSON(prompts):
  genai.configure(api_key=config('GEMINI_API'))
  generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "application/json",
        }
  model = genai.GenerativeModel(
            model_name="gemini-2.5-flash-lite",
            generation_config=generation_config
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
    """
    Robust resume extractor using both AI (Gemini) and rule-based methods.
    Handles file-like objects in-memory, validates AI response,
    cleans text, normalizes experience, and retries AI extraction.
    """

    
    
    file_extension = os.path.splitext(file.name)[1].lower()
    extracted_textinfo = []
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
        for chunk in file.chunks():
            temp_file.write(chunk)
        temp_file.flush()
        temp_file_path = temp_file.name
    # -----------------------------
    # Step 1: Extract text from resume
    # -----------------------------
    try:
        if file_extension == ".pdf":
            extracted_textinfo = TextConverter.pdf_to_text(temp_file_path)
        elif file_extension == ".doc":
            extracted_textinfo = TextConverter.doc_to_text(temp_file_path)
        elif file_extension == ".docx":
            extracted_textinfo = TextConverter.docx_to_text(temp_file_path)
        elif file_extension in [".jpg", ".jpeg", ".png"]:
            extracted_textinfo = TextConverter.img_to_text(temp_file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    except Exception as e:
        logging.error(f"[Text Extraction] Error extracting text from {file.name}: {e}", exc_info=True)
        raise

    # -----------------------------
    # Step 2: Clean text for AI processing
    # -----------------------------
    cleaned_text = "\n".join(extracted_textinfo)
    cleaned_text = ''.join(ch if ch.isprintable() else ' ' for ch in cleaned_text)

    # Truncate to avoid exceeding AI token limits (Gemini ~8K tokens)
    max_length = 15000  # adjust as needed
    if len(cleaned_text) > max_length:
        cleaned_text = cleaned_text[:max_length]

    # -----------------------------
    # Step 3: AI Extraction with retry
    # -----------------------------
    ai_response = {}
    max_retries = 3
    for attempt in range(max_retries):
        try:
            ai_response = Resume_Date_As_JSON(cleaned_text)
            if isinstance(ai_response, dict):
                break
            else:
                raise ValueError("AI response is not a dictionary")
        except Exception as e:
            logging.warning(f"[AI Extraction] Attempt {attempt+1} failed for {file.name}: {e}", exc_info=True)
            time.sleep(2 ** attempt)
            ai_response = {}
    else:
        logging.error(f"[AI Extraction] All attempts failed for {file.name}")

    # -----------------------------
    # Step 4: Rule-based Extraction
    # -----------------------------
    try:
        rule_based_data = {
            "Name": DataExtraction.extract_name(extracted_textinfo),
            "Phone": DataExtraction.extract_phonenumbers(extracted_textinfo),
            "Email": DataExtraction.extract_emails(extracted_textinfo),
            "FileName": DataExtraction.extract_file_name(file)
        }
    except Exception as e:
        logging.error(f"[Rule-based Extraction] Failed for {file.name}: {e}", exc_info=True)
        rule_based_data = {}

    # -----------------------------
    # Step 5: Merge AI + Rule-based data
    # -----------------------------
    merged = {
        "Name": ai_response.get("Name") or rule_based_data.get("Name") or None,
        "Phone": rule_based_data.get("Phone") or "",
        "Email": ai_response.get("Email") or rule_based_data.get("Email") or "",
        "Highest_Educational_Degree": ai_response.get("Highest_Educational_Degree", ""),
        "Passing_Year": ai_response.get("Passing_Year", ""),
        "Highest_Education_Degree_Institution": ai_response.get("Highest_Education_Degree_Institution", ""),
        "Professional_Degree": ai_response.get("Professional_Degree", ""),
        "Experience": ai_response.get("Experience") if isinstance(ai_response.get("Experience"), list) else [],
        "Permanent_Address": ai_response.get("Permanent_Address", ""),
        "File_Name": rule_based_data.get('FileName')
    }

    return merged

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
                    response = ResumeExtractor(file)
                    
                    candidate_info = CandidateInitialInformation.objects.create(
                        name=response.get("Name", "").title() or None,
                        mobile_no=response.get("Phone", ""),
                        email=response.get("Email", ""),
                        highest_education_degree=response.get("Highest_Educational_Degree", ""),
                        highest_education_degree_institution=response.get("Highest_Education_Degree_Institution", ""),
                        professional_education_degree=response.get("Professional_Degree", ""),
                        passing_year=response.get("Passing_Year", ""),
                        experience=response.get("Experience", []),
                        address=response.get("Permanent_Address", ""),
                        status = "shortlisted",
                        resume=file  # save actual file
                    )
                    candidate_info.jobs.set(jobs)
                    
                    candidate = Candidate.objects.create(
                        name=response.get("Name", "").title() or None,
                        mobile=response.get("Phone", ""),
                        email=response.get("Email", ""),
                        filename=file.name,
                        candidate_initial_info=candidate_info,
                        attendance_status='absent',
                        interview_schedule=interview_schedule
                    )
                    
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
    candidate_data = candidate_google_sheet.candidate_details_data # Fetch data from Google Sheet
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

def candidate_list_google_sheet(request, pk):
    try:
        job = get_object_or_404(Job, id=pk)

        # filter jobs with same google_sheet_id
        jobs = Job.objects.filter(google_sheet_id=job.google_sheet_id)

        qs = CandidateInitialInformation.objects.filter(jobs__in=jobs).distinct()

        # extra filters (from query params)
        status = request.GET.get("status")
        if status:
            qs = qs.filter(status=status)  # assumes you have a 'status' field

        candidate_data = list(qs.values("id", "name", "email", "status"))  # select only useful fields

    except Exception as e:
        return JsonResponse([{"error": f"an error occurred: {e}"}], safe=False)
    return JsonResponse(candidate_data, safe=False)


def candidates_api(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    candidates = CandidateInitialInformation.objects.filter(jobs=job).distinct().order_by(
        Case(
            When(status="New", then=Value(0)),   # New comes first
            default=Value(1),
            output_field=IntegerField(),
        ),
        "-upload_date",  # then order by latest updated
    )

    status = request.GET.get("status")
    if status:
        candidates = candidates.filter(status=status)

    data = []
    for candidate in candidates:
        candidate_dict = {
            "id": candidate.id,
            "name": candidate.name,
            "mobile_no": candidate.mobile_no,
            "email": candidate.email,
            "highest_education_degree": candidate.highest_education_degree,
            "highest_education_degree_institution": candidate.highest_education_degree_institution,
            "professional_education_degree": candidate.professional_education_degree,
            "total_experience": candidate.total_experience,
            "current_designation": candidate.current_designation,
            "current_organization": candidate.current_organization,
            "current_location": candidate.current_location,
            "passing_year": candidate.passing_year,
            "experience": candidate.experience,
            "address": candidate.address,
            "resume": candidate.resume.url if candidate.resume else None,
            "upload_date": candidate.upload_date,
            "status": candidate.status,
            'job_title': candidate.jobs.first().job_title,
        }

        existing_candidate = Candidate.objects.filter(mobile=candidate.mobile_no).first()
        if existing_candidate:
            candidate_dict.update({
                "invitation_status": existing_candidate.invitation_status,
                'interview_date': existing_candidate.interview_schedule.interview_date.isoformat() if existing_candidate.interview_schedule else None,
                "interview_attendance": existing_candidate.attendance_status,
                "interview_status": existing_candidate.initial_interview_status,
            })
        else:
            candidate_dict.update({
                "interview_date": None,
                "interview_attendance": None,
                "interview_status": None,
            })

        data.append(candidate_dict)
    return JsonResponse(data, safe=False)


def all_candidates_api(request):
    """Return all CandidateInitialInformation records as JSON.

    Kept lightweight: returns similar fields as `candidates_api` but for all jobs
    and supports optional 'status' filter via query params.
    """
    try:
        candidates = CandidateInitialInformation.objects.all().distinct().order_by(
            Case(
                When(status="New", then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            ),
            "-upload_date",
        )

        status = request.GET.get("status")
        if status:
            candidates = candidates.filter(status=status)

        data = []
        for candidate in candidates:
            candidate_dict = {
                "id": candidate.id,
                "name": candidate.name,
                "mobile_no": candidate.mobile_no,
                "email": candidate.email,
                "highest_education_degree": candidate.highest_education_degree,
                "highest_education_degree_institution": candidate.highest_education_degree_institution,
                "professional_education_degree": candidate.professional_education_degree,
                "total_experience": candidate.total_experience,
                "current_designation": candidate.current_designation,
                "current_organization": candidate.current_organization,
                "current_location": candidate.current_location,
                "passing_year": candidate.passing_year,
                "experience": candidate.experience,
                "address": candidate.address,
                "resume": candidate.resume.url if candidate.resume else None,
                "upload_date": candidate.upload_date.isoformat() if getattr(candidate, 'upload_date', None) else None,
                "jobs": list(candidate.jobs.values_list('id', flat=True)) if hasattr(candidate, 'jobs') else [],
                "status": candidate.status,
                'job_title': candidate.jobs.first().job_title if candidate.jobs.exists() else None,
            }

            existing_candidate = Candidate.objects.filter(mobile=candidate.mobile_no).first()
            if existing_candidate:
                candidate_dict.update({
                    "invitation_status": existing_candidate.invitation_status,
                    'interview_date': existing_candidate.interview_schedule.interview_date.isoformat() if existing_candidate.interview_schedule else None,
                    "interview_attendance": existing_candidate.attendance_status,
                    "interview_status": existing_candidate.initial_interview_status,
                })
            else:
                candidate_dict.update({
                    "interview_date": None,
                    "interview_attendance": None,
                    "interview_status": None,
                })

            data.append(candidate_dict)
    except Exception as e:
        return JsonResponse([{"error": f"an error occurred: {e}"}], safe=False)

    return JsonResponse(data, safe=False)


class CandidatesList(ListView):
    model = CandidateInitialInformation
    template_name = "candidates/candidates_list_sorting.html"
    context_object_name = "candidates"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["jobs"] = Job.objects.all()  # for dropdown filter
        return context

def jobs_api(request):
    # Only jobs that have a Google Sheet linked
    jobs = list(Job.objects.filter(google_sheet_id__isnull=False, open_status=True).distinct().values("id", "job_title", "department", "job_location", "unit__short_name"))
    return JsonResponse(jobs, safe=False)

def update_candidate_status(request, candidate_id):
    if request.method == 'POST':
        candidate = get_object_or_404(CandidateInitialInformation, id=candidate_id)
        new_status = request.POST.get('status')
        candidate.status = new_status
        candidate.upload_date = timezone.now()
        candidate.save()
        return JsonResponse({'success': True, 'new_status': new_status})
    return JsonResponse({'success': False}, status=400)

def transfer_candidate_for_another_job(request):
    if request.method == "POST":
        candidate_id = request.POST.get("candidate_id")
        new_job_ids = request.POST.getlist("job_id")
        

        if not candidate_id or not new_job_ids:
            return JsonResponse({"success": False, "error": "Candidate or job not provided"}, status=400)

        candidate = get_object_or_404(CandidateInitialInformation, id=candidate_id)
        new_jobs = Job.objects.filter(id__in=new_job_ids)

        # Add candidate to the new job (ManyToMany)
        candidate.jobs.set(new_jobs)
        candidate.save()

        return JsonResponse({"success": True, "message": f"{candidate.name} transferred to {', '.join(job.job_title for job in new_jobs)}"})

    return JsonResponse({"success": False, "error": "Invalid request method"}, status=400)

def include_in_interview_schedule(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request method"}, status=400)

    interview_id = request.GET.get('interview_id')
    interview_schedule = get_object_or_404(InterviewSchedule, id=interview_id)

    candidate_ids = request.GET.getlist("candidate_ids")

    # Get candidate initial info records
    candidates_info = CandidateInitialInformation.objects.filter(id__in=candidate_ids)

    added_count = 0

    for candidate_info in candidates_info:
        email = candidate_info.email if candidate_info.email else "notfound@gmail.com"

        # Check if candidate already exists
        candidate_qs = Candidate.objects.filter(
            mobile=candidate_info.mobile_no,
            interview_schedule=interview_schedule
        )

        if candidate_qs.exists():
            # Pick the first existing candidate
            candidate = candidate_qs.first()
            created = False
        else:
            # Create a new candidate
            candidate = Candidate.objects.create(
                mobile=candidate_info.mobile_no,
                email=email,
                name=candidate_info.name,
                attendance_status='absent',
                candidate_initial_info=candidate_info,
                interview_schedule=interview_schedule
            )
            created = True

        # Always sync jobs
        candidate.job.set(candidate_info.jobs.all())

        if created:
            added_count += 1

    return JsonResponse({
        "success": True,
        "message": f"{added_count} candidates added to the interview schedule."
    })

class CandidateInitialInformationDetailView(DetailView):
    model = CandidateInitialInformation
    template_name = "candidates/candidate_initial_info_detail.html"
    context_object_name = "candidate"
    


