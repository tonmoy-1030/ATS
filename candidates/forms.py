from django import forms
import django_filters.widgets
from .models import Offer, Candidate
from django.forms import ValidationError
from django.shortcuts import get_object_or_404
import django_filters
from jobs.models import Job
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Div, Submit

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class FileFieldForm(forms.Form):
    file_field = MultipleFileField()

class JobOfferCreateForm(forms.ModelForm):
    job = forms.ModelChoiceField(queryset=Job.objects.none(), empty_label="Select Job")

    class Meta:
        model = Offer
        fields = ['job', 'offered_designation', 'joining_date', 'offer_status', 'remarks']
        widgets = {
            'joining_date': forms.DateInput(attrs={'type': 'date'}),
            'remarks': forms.Textarea(attrs={'rows': 4}),
        }
        
    def __init__(self, *args, **kwargs):
        candidate_id = kwargs.pop('candidate_id', None)
        super().__init__(*args, **kwargs)
        self.candidate_id = candidate_id 
        if candidate_id:
            candidate = get_object_or_404(Candidate, pk=candidate_id)
            self.fields['job'].queryset = candidate.final_interview.job.filter(open_status=True)
            
              
    def clean(self):
        cleaned_data = super().clean()
        job = cleaned_data.get('job')
        offer_status = cleaned_data.get('offer_status')

        if job and offer_status == 'accepted':
            if job.offers.filter(offer_status='accepted').count() >= job.no_of_position:
                raise forms.ValidationError("Offer cannot be made as there are no available positions.")
        return cleaned_data
    
class JobOfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ['job','offered_designation','joining_date','offer_status', 'remarks']
        
        widgets = {
            'joining_date': forms.DateInput(
                attrs={
                    'type': 'date'
                }
            )
        }
        
    def __init__(self, *args, **kwargs):
        candidate_id = kwargs.pop('candidate_id', None)
        super().__init__(*args, **kwargs)
        self.candidate_id = candidate_id 
        if candidate_id:
            candidate = get_object_or_404(Candidate, pk=candidate_id)
            self.fields['job'].queryset = candidate.final_interview.job.filter()
            
              
    def clean(self):
        cleaned_data = super().clean()
        job = cleaned_data.get('job')
        offer_status = cleaned_data.get('offer_status')

        if job and offer_status == 'accepted':
            if job.offers.filter(offer_status='accepted').count() >= job.no_of_position:
                raise forms.ValidationError("Offer cannot be made as there are no available positions.")
        return cleaned_data

class JobOfferFilter(django_filters.FilterSet):
    OFFER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    name = django_filters.CharFilter(field_name='candidate__name', 
                                     lookup_expr='icontains', 
                                     label="Candidate Name")
    unit = django_filters.ChoiceFilter(field_name='candidate__job__unit', choices=[], 
                                        
                                       )
    offer_status = django_filters.ChoiceFilter(field_name='offer_status', 
                                               choices=OFFER_STATUS_CHOICES, 
                                              
                                               )
    Joining_date = django_filters.DateFromToRangeFilter(field_name='joining_date',
                                                    widget=django_filters.widgets.RangeWidget(
                                                    attrs={
                                                            'type': 'date'
                                                        }
                                                    )
                                                )  
    
    def get_unit_choices(self):
        unique_units = Job.objects.values_list('unit', flat=True).distinct()
        choices = [(unit, unit) for unit in unique_units]
        return choices
    
    class Meta:
        model = Offer
        fields = ['name', 'unit', 'offer_status', 'Joining_date']
        
        widgets = {
            'name':forms.TextInput(attrs={'class':'form-control'}),
            'unit':forms.Select(attrs={'class':'form-select'}),
            'offer_status':forms.Select(attrs={'class':'form-select'}),
            
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['unit'].extra['choices'] = self.get_unit_choices()

        
class InitialCandidateUpdateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['name','invitation_status', 'attendance_status', 'initial_interview_status']
        
        widgets = {
            'name':forms.TextInput(attrs={'class':'form-control'}),
            'invitation_status':forms.Select(attrs={'class':'form-select'}),
            'attendance_status':forms.Select(attrs={'class':'form-select'}),
            'initial_interview_status':forms.Select(attrs={'class':'form-select'}),
        }

        
class FinalCandidateUpdateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['name','final_interview_attendance', 'final_interview_status']
        
        widgets = {
            'name':forms.TextInput(attrs={'class':'form-control'}),
            'final_interview_attendance':forms.Select(attrs={'class':'form-select'}),
            'final_interview_status':forms.Select(attrs={'class':'form-select'}),
        }