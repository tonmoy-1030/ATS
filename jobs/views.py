
from typing import Any
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.messages.views import SuccessMessageMixin
from .models import Job, InterviewSchedule, FinalInterviewSchedule, BusinessUnit
from django.views.generic import DetailView, CreateView, UpdateView, ListView, DeleteView
from candidates.models import Candidate, Offer, CandidateInitialInformation
from django.urls import reverse
from django.db.models import Count, Subquery
from django.http import HttpResponse, JsonResponse
from .forms import (RequisitionForm, InterviewFilter, FinalInterviewFilter,
                    ScheduleForm, UpdateScheduleForm, UpdateFinalScheduleForm,
                    HCRFFilter, UpdateRequisitionForm)
from django.utils import timezone
from employees.models import Employee
from collections import defaultdict
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

# unauthorized page

def unauthorized(request):
    return render(request, 'jobs/unauthorized.html')


# Logout Page
def logoutPage(request):
    return render(request, "jobs/logout.html")

# job
class home( ListView):
    model = Job
    template_name = 'jobs/home.html'
    offer_model = Offer    
    employee_model = Employee

    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        current_month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        yearly_labels = []
        yearly_data = []
        monthly_labels = []
        monthly_data = []
        context = super().get_context_data(**kwargs)
        
        #Vacant Position
        requisitions = Job.objects.filter(open_status=True)
        grouped_requisitions = defaultdict(list)
        unit_sums = []

        unit_sums_dict = {}

        for req in requisitions:
            grouped_requisitions[req.unit].append(req)
            if req.unit not in unit_sums_dict:
                unit_sums_dict[req.unit] = {'unit': req.unit, 'total_positions': 0, 'total_filled': 0}
            unit_sums_dict[req.unit]['total_positions'] += req.no_of_position
            unit_sums_dict[req.unit]['total_filled'] += req.filled_positions()
        
        for unit, sums in unit_sums_dict.items():
            unit_sums.append(sums)
            
        #***Vacant Position end ***#

        upcoming_joining = Offer.objects.filter(offer_status='Accepted', joining_date__gte = timezone.now(), candidate__employee__isnull=True).order_by("joining_date", 'candidate__job__unit').distinct()
        grouped_joining = defaultdict(list)
        joining_unit_sum = []
        joining_unit_sum_dict = {}
        
        for position in upcoming_joining:
            grouped_joining[position.job.unit].append(position)
            
            if position.job.unit not in joining_unit_sum_dict:
                joining_unit_sum_dict[position.job.unit] = {'unit':position.job.unit, 'total_number': 0}
            joining_unit_sum_dict[position.job.unit]['total_number'] = Offer.objects.filter(job__unit=position.job.unit, offer_status='Accepted', joining_date__gte = timezone.now(), candidate__employee__isnull=True).distinct().count()
            
        for unit, sums in joining_unit_sum_dict.items():
            joining_unit_sum.append(sums)
        
        
        
        employee_counts = Employee.objects.filter(DOJ__year=timezone.now().year).values('unit').annotate(count=Count('id'))
        employees_joined_current_month = Employee.objects.filter(DOJ__gte=current_month_start).values('unit').annotate(count=Count('id'))      
        employee_counts_dict = {employee['unit']: employee['count'] for employee in employee_counts}
        employee_counts_monthly_dict = {employee['unit']: employee['count'] for employee in employees_joined_current_month}
        schedules = InterviewSchedule.objects.filter(interview_date__gte=timezone.now().date()).order_by('-interview_date')
        final_schedules = FinalInterviewSchedule.objects.filter(interview_date__gte=timezone.now().date()).order_by('-interview_date')
        Total_employee_yearly = Employee.objects.filter(DOJ__year=timezone.now().year).count()
        Total_employee_monthly = Employee.objects.filter(DOJ__gte=current_month_start).count()

        
        for key, value in employee_counts_dict.items():
            unit = BusinessUnit.objects.get(id=key)            
            yearly_labels.append(unit.short_name)
            yearly_data.append(value)
            
        for key, value in employee_counts_monthly_dict.items():
            unit = BusinessUnit.objects.get(id=key)  
            monthly_labels.append(unit.short_name)
            monthly_data.append(value) 

        context['grouped_requisitions'] = dict(grouped_requisitions)
        context['unit_sums'] = unit_sums
        
        context['grouped_joining'] = dict(grouped_joining)
        context['joining_unit_sum'] = joining_unit_sum
        
        context['yearly_labels'] = yearly_labels
        context['yearly_data'] = yearly_data
        context['monthly_labels'] = monthly_labels
        context['monthly_data'] = monthly_data
        context['schedules'] = schedules
        context['final_schedules'] = final_schedules
        context['Total_employee_monthly'] = Total_employee_monthly
        context['Total_employee_yearly'] = Total_employee_yearly
        return context
 

class expands_requisition(ListView):
    model = Job
    template_name = 'jobs/expend_requisition.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        requisitions = Job.objects.filter(open_status=True)
        grouped_requisitions = defaultdict(list)
        unit_sums = []

        unit_sums_dict = {}

        for req in requisitions:
            grouped_requisitions[req.unit].append(req)
            if req.unit not in unit_sums_dict:
                unit_sums_dict[req.unit] = {'unit': req.unit, 'total_positions': 0, 'total_filled': 0}
            unit_sums_dict[req.unit]['total_positions'] += req.no_of_position
            unit_sums_dict[req.unit]['total_filled'] += req.filled_positions()
        
        for unit, sums in unit_sums_dict.items():
            unit_sums.append(sums)

        context['grouped_requisitions'] = dict(grouped_requisitions)
        context['unit_sums'] = unit_sums
        
        return context
 
    
class expands_joining_list(ListView):
    model = Job
    template_name = 'jobs/expend_joining_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        upcoming_joining = Offer.objects.filter(offer_status='Accepted', joining_date__gte = timezone.now(), candidate__employee__isnull=True).order_by("joining_date", 'candidate__job__unit').distinct()
        grouped_joining = defaultdict(list)
        joining_unit_sum = []
        joining_unit_sum_dict = {}
        
        for position in upcoming_joining:
            grouped_joining[position.job.unit].append(position)
            
            if position.job.unit not in joining_unit_sum_dict:
                joining_unit_sum_dict[position.job.unit] = {'unit':position.job.unit, 'total_number': 0}
            joining_unit_sum_dict[position.job.unit]['total_number'] = Offer.objects.filter(job__unit=position.job.unit, offer_status='Accepted', joining_date__gte = timezone.now(), candidate__employee__isnull=True).distinct().count()
            
        for unit, sums in joining_unit_sum_dict.items():
            joining_unit_sum.append(sums)

        context['grouped_joining'] = dict(grouped_joining)
        context['joining_unit_sum'] = joining_unit_sum
        
        return context
    

    
        
class HeadCountListView(ListView):
    model = Job
    template_name = 'jobs/job_list.html'    
    context_object_name = 'requisitions'
    # ordering = ['-open_status', 'posting_date']
    paginate_by = 15
    
    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = HCRFFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs.distinct().order_by('-open_status', 'posting_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset
        return context
    

class HeadcountCreateview(SuccessMessageMixin, CreateView):
    model = Job
    form_class = RequisitionForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        requisitions_list = Job.objects.order_by('-posting_date')
        context['requisitions'] = requisitions_list
        return context
    
    def get_success_url(self):
        return reverse('jobs:create-headcount')
    success_message = "%(job_title)s for %(department)s department in %(unit)s  was created successfully"    
    
    
    
class JobDetailView(DetailView):
    model = Job

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        job = self.object
        interviews = InterviewSchedule.objects.filter(job=job)
        Final_interviews = FinalInterviewSchedule.objects.filter(job=job)
        context['interviews'] = interviews
        context['final_interviews'] = Final_interviews
        return context
    
    
class JobUpdateView(SuccessMessageMixin, UpdateView):
    model = Job
    form_class = UpdateRequisitionForm
    def get_success_url(self):
        return reverse('jobs:job_details', kwargs={'pk': self.object.pk})
    
    success_message = "%(job_title)s for %(department)s department in %(unit)s  is updated successfully"       
    
 
#Inital Interivew List
class InitialInterviewList(ListView):
    model = InterviewSchedule
    template_name = 'jobs/intialinterviewList.html'
    context_object_name ='schedules'
    paginate_by = 11

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = InterviewFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs.distinct().order_by('-interview_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context

#Final Interivew List
class FinalInitialInterviewList(ListView):
    model = FinalInterviewSchedule
    template_name = 'jobs/finalinterviewList.html'
    context_object_name ='schedules'
    paginate_by = 11

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = FinalInterviewFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs.distinct().order_by('-interview_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context
#end# 

#initial Interview schedule view   
    

class ScheduleDetailview(DetailView):
    model = InterviewSchedule
    
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        interview_schedule = self.object
        all_candidates = Candidate.objects.all()
        duplicate_mobiles = all_candidates.values('mobile').annotate(count=Count('mobile')).filter(count__gt=1).values_list('mobile', flat=True)
        candidates = all_candidates.filter(interview_schedule=interview_schedule)       
        context['candidates'] = candidates
        context['duplicate_mobiles'] = duplicate_mobiles
        return context

class ScheduleDeleteview(DeleteView):
    model = InterviewSchedule
        
    def get_success_url(self):
        return reverse('jobs:initial_interview_list')
    
class ScheduleListview(ListView):
    model = InterviewSchedule
    template_name = 'jobs/home.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        schedules = InterviewSchedule.objects.filter(interview_date__gte=timezone.now()).order_by('-interview_date')
        context['schedules'] = schedules
        return context
    
#final Interview Schedule view


class FinalScheduleDetailview(DetailView):
    model = FinalInterviewSchedule
    
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        final_interview_schedule = self.object
        
        candidates = Candidate.objects.filter(final_interview=final_interview_schedule)
        context['candidates'] = candidates
        return context

class FinalScheduleDeleteview(DeleteView):
    model = FinalInterviewSchedule
        
    def get_success_url(self):
        return reverse('jobs:final_interview_list')

class ShortListedCandidate(ListView):
    template_name = 'jobs/shortlisted_candidates.html'
    context_object_name = 'shortliested_candidates'
    
    def get_queryset(self):
        interview_schedule = get_object_or_404(FinalInterviewSchedule, pk=self.kwargs['pk'])
        jobs = interview_schedule.job.all()        
        return Candidate.objects.filter(interview_schedule__job__in=jobs,
                                        initial_interview_status='Forwarding for the next Interivew') \
                                        .exclude(final_interview__isnull=False).distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        interview_schedule = get_object_or_404(FinalInterviewSchedule, pk=self.kwargs['pk'])
        jobs = interview_schedule.job.all()
        context['job'] = jobs
        context['interview'] = get_object_or_404(FinalInterviewSchedule, pk=self.kwargs['pk'] )
        return context  

def finalize_final_interview(request, pk):
    if request.method == 'POST':
        selected_candidate_ids = request.POST.getlist('selected_candidates')
        final_interview = get_object_or_404(FinalInterviewSchedule, pk=pk)
        Candidate.objects.filter(id__in=selected_candidate_ids).update(final_interview=final_interview)
        return redirect('jobs:final_interview_details', pk=final_interview.pk)
    return HttpResponse("Invalid request method.")

def remove_from_final_interview(request, pk):
    if request.method == 'POST':
        candidate = get_object_or_404(Candidate, pk=pk)
        final_interview = get_object_or_404(FinalInterviewSchedule, pk=candidate.final_interview.pk)
        if hasattr(candidate, 'offer'):
            candidate.offer.delete()
            candidate.final_interview = None
            candidate.final_interview_status = None
            candidate.final_interview_attendance = None
            candidate.save()
        else:
            candidate.final_interview = None
            candidate.final_interview_status = None
            candidate.final_interview_attendance = None
            candidate.save()
        
        return redirect('jobs:final_interview_details', pk=final_interview.pk)
    return HttpResponse("Invalid request method.")


def create_schedule(request):
    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            jobs = form.cleaned_data['jobs']
            interview_type = form.cleaned_data['interview_type']
            interview_date = form.cleaned_data['interview_date']
            interviewers = form.cleaned_data['interviewer']

            if interview_type == 'Initial':
                schedule = InterviewSchedule(interview_type=interview_type, interview_date=interview_date)
            else:
                schedule = FinalInterviewSchedule(interview_type=interview_type, interview_date=interview_date)
                
            schedule.save()
            schedule.job.set(jobs)
            schedule.interviewer.set(interviewers)

            messages.success(request, 'Schedule created successfully.')
            form = ScheduleForm()    
    else:
        form = ScheduleForm()
    
    return render(request, 'jobs/schedule_form.html', {'form': form})



class ScheduleUpdateView(UpdateView):
    model = InterviewSchedule
    form_class = UpdateScheduleForm
    template_name = 'jobs/schedule_form.html'
    success_url = ('/initial_interview')
    
    def form_valid(self, form):
        schedule = form.save(commit=False)
        schedule.save()
        form.save_m2m()
        
        messages.success(self.request, 'Schedule updated successfully.')
        return super().form_valid(form)
    
class FinalScheduleUpdateView(UpdateView):
    model = FinalInterviewSchedule
    form_class = UpdateFinalScheduleForm
    template_name = 'jobs/schedule_form.html'
    success_url = ('/final_interview')

    def form_valid(self, form):
        schedule = form.save(commit=False)
        schedule.save()
        form.save_m2m()
        messages.success(self.request, 'Schedule updated successfully.')
        return super().form_valid(form)


def load_jobs(request):
    unit = request.GET.get('unit')
    jobs = Job.objects.filter(unit=unit, open_status=True)
    job_list = []
    for job in jobs:
        job_dict = {
            "job_id":job.id,
            "designation": job.job_title,
            "unit": job.unit.name,
            "location": job.job_location
        }
        job_list.append(job_dict)
    return JsonResponse(job_list, safe=False)

def display_candidates(request, pk):
    # Already assigned candidates for this interview
    existing_candidates = Candidate.objects.filter(
        interview_schedule_id=pk
    ).values_list("candidate_initial_info__id", flat=True)

    interview_schedule = get_object_or_404(InterviewSchedule, id=pk)
    interview_jobs = interview_schedule.job.all()
    
   
    # Query shortlisted candidates for the same jobs, exclude already added ones
    qs = (
        CandidateInitialInformation.objects
        .filter(jobs__in=interview_jobs, status="shortlisted")
        .exclude(id__in=existing_candidates)
        .prefetch_related("jobs")
        .distinct()
    )
    candidates = list({c.id: c for c in qs}.values())

    data = [
        {
            "id": c.id,
            "name": c.name,
            "mobile_no": c.mobile_no,
            "email": c.email,
            "status": c.status,
            "job_titles": c.jobs.first().job_title,
        }
        for c in candidates
    ]

    return JsonResponse({"candidates": data}, safe=False)
