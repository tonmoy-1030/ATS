from django import forms
from candidates.models import Candidate
from .models import Job, InterviewSchedule, FinalInterviewSchedule
from django_select2 import forms as s2forms
from employees.models import Employee
from django.db.models import Q
import django_filters


class DatePickerInput(forms.DateInput):
        input_type = 'date'


class Jobwidgets(s2forms.ModelSelect2MultipleWidget):
    model = Job
    search_fields = [
        "job_title__icontains",
        "unit__icontains",
    ]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs['data-placeholder'] = "Select vacant Position..."
        self.queryset = Job.objects.filter(open_status=True)
        
class FinalInterviewCandidateSelectionForm(forms.Form):
    class Meta:
        model = Candidate 
        fields = ['selected_candidates']

    selected_candidates = forms.ModelMultipleChoiceField(
        queryset=Candidate.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )

    pk = forms.IntegerField(widget=forms.HiddenInput)
    

class Employeewidgets(s2forms.ModelSelect2MultipleWidget):
    model = Employee
    search_fields = [
        "name__icontains",
        "designation__icontains",
    ]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs['data-placeholder'] = "Select interviewers..."
        self.attrs['data-minimum-input-length'] = 0
        self.attrs['class'] = 'form-select'
 
 
class HCRFFilter(django_filters.FilterSet):
    position = django_filters.CharFilter(field_name="job_title")
    unit = django_filters.ChoiceFilter( field_name='unit', choices=[])
    open_status = django_filters.ChoiceFilter(field_name='open_status', choices = [('True', 'Open'), ('False', 'Close')])
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['unit'].extra['choices'] = self.get_unit_choices()
        
    def get_unit_choices(self):
        unique_units = Job.objects.values_list('unit__id', 'unit__name').distinct()
        choices = [(unit_id, unit_name) for unit_id, unit_name in unique_units]
        return choices
 
    class Meta:
        model = Job
        fields = ['position','unit', 'open_status']

               
        
class RequisitionForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['job_title', 'department', 'unit', 'job_location', 'posting_date','types', 'no_of_position', 'remarks']
        widgets = { 
                   'posting_date' : DatePickerInput(),
                   'remarks': forms.Textarea(attrs={'rows':2}),
                   }


class ScheduleForm(forms.Form):
    unit = forms.ChoiceField(
        choices=[("", "Select a unit")],
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_unit', "placeholder":"Select Unit"})
    )
    jobs = forms.ModelMultipleChoiceField(
        queryset=Job.objects.none(),
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'id': 'id_jobs'}),
        required=True
    )
    interview_type = forms.ChoiceField(
        choices=[('', 'Select interview type'),('Initial', 'Initial Interview'), ('Final', 'Final Interview')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    interview_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})
    )
    
    interviewer = forms.ModelMultipleChoiceField(
        queryset=Employee.objects.all(),
        widget=s2forms.ModelSelect2MultipleWidget(
            model=Employee,
            search_fields=['name__icontains'],
            attrs={'class': 'form-select', 'id':'interview'},
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['unit'].choices += [
            (unit_id, unit_name) for (unit_id, unit_name) in Job.objects.values_list('unit__id', 'unit__name').distinct()
        ]
        if 'unit' in self.data:
            try:
                unit = self.data.get('unit')
                self.fields['jobs'].queryset = Job.objects.filter(unit=unit, open_status=True)
            except (ValueError, TypeError):
                self.fields['jobs'].queryset = Job.objects.none()
        else:
            self.fields['jobs'].queryset = Job.objects.none()
                
class UpdateScheduleForm(forms.ModelForm):
    unit = forms.ChoiceField(
        choices=[("", "Select a unit")],
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_unit', "placeholder":"Select Unit"})
    )
    job = forms.ModelMultipleChoiceField(
        queryset=Job.objects.none(),
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'id': 'id_jobs'}),
        required=True
    )
    class Meta:
        model = InterviewSchedule
        fields = ['unit','job','interview_date', 'interviewer']
        widgets = {
            
            'job':forms.Select(attrs={'class': 'form-select'}),
            'interview_type': forms.Select(attrs={'class': 'form-select'}),
            'interview_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'interviewer': Employeewidgets
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['unit'].choices += [
            (unit_id, unit_name) for (unit_id, unit_name) in Job.objects.values_list('unit__id', 'unit__name').distinct()
        ]

        if self.instance.pk:
            initial_jobs = self.instance.job.all()
            unit = initial_jobs.first().unit if initial_jobs.exists() else None
            if unit:
                self.fields['unit'].initial = unit 
                self.fields['job'].queryset = Job.objects.filter(unit=unit, open_status=True) | initial_jobs
            else:
                self.fields['job'].queryset = initial_jobs
        elif 'unit' in self.data:
            try:
                unit = self.data.get('unit')
                self.fields['job'].queryset = Job.objects.filter(unit=unit, open_status=True)
            except (ValueError, TypeError):
                self.fields['job'].queryset = Job.objects.none()
        else:
            self.fields['job'].queryset = Job.objects.none()


    def clean_unit(self):
        return self.cleaned_data['unit'] if self.cleaned_data['unit'] else None
            
class UpdateFinalScheduleForm(forms.ModelForm):
    unit = forms.ChoiceField(
        choices=[("", "Select a unit")],
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_unit', "placeholder":"Select Unit"})
    )
    job = forms.ModelMultipleChoiceField(
        queryset=Job.objects.none(),
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'id': 'id_jobs'}),
        required=True
    )
    class Meta:
        model = FinalInterviewSchedule
        fields = ['unit','job','interview_date', 'interviewer']
        widgets = {
            
            'job':forms.Select(attrs={'class': 'form-select'}),
            'interview_type': forms.Select(attrs={'class': 'form-select'}),
            'interview_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'interviewer': Employeewidgets
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['unit'].choices += [
            (unit, unit) for unit in Job.objects.values_list('unit', flat=True).distinct()
        ]

        if self.instance.pk:
            initial_jobs = self.instance.job.all()
            unit = initial_jobs.first().unit if initial_jobs.exists() else None
            if unit:
                self.fields['unit'].initial = unit 
                self.fields['job'].queryset = Job.objects.filter(unit=unit, open_status=True) | initial_jobs
            else:
                self.fields['job'].queryset = initial_jobs
        elif 'unit' in self.data:
            try:
                unit = self.data.get('unit')
                self.fields['job'].queryset = Job.objects.filter(unit=unit, open_status=True)
            except (ValueError, TypeError):
                self.fields['job'].queryset = Job.objects.none()
        else:
            self.fields['job'].queryset = Job.objects.none()


    def clean_unit(self):
        return self.cleaned_data['unit'] if self.cleaned_data['unit'] else None

class InterviewFilter(django_filters.FilterSet):
    unit = django_filters.ChoiceFilter( field_name='job__unit', choices=[])
    interview_date = django_filters.DateFromToRangeFilter(field_name='interview_date',widget=django_filters.widgets.RangeWidget(
                                                    attrs={
                                                            'type': 'date'
                                                        }
                                                    ))
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['unit'].extra['choices'] = self.get_unit_choices()
      
        
    def get_unit_choices(self):
        unique_units = Job.objects.values_list('unit__id', 'unit__name').distinct()
        choices = [(unit_id, unit_name) for unit_id, unit_name in unique_units]
        return choices
 
    class Meta:
        model = InterviewSchedule
        fields = ['interview_type','interview_date', 'unit']
        

class FinalInterviewFilter(django_filters.FilterSet):
    unit = django_filters.ChoiceFilter(field_name='job__unit', choices=[])
    interview_date = django_filters.DateFromToRangeFilter(field_name='interview_date',widget=django_filters.widgets.RangeWidget(
                                                    attrs={
                                                            'type': 'date'
                                                        }
                                                    )
                                                          )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['unit'].extra['choices'] = self.get_unit_choices()

    def get_unit_choices(self):
        unique_units = Job.objects.values_list('unit__id', 'unit__name').distinct()
        choices = [(unit_id, unit_name) for unit_id, unit_name in unique_units]
        return choices

    class Meta:
        model = FinalInterviewSchedule
        fields = ['interview_date', 'unit']
