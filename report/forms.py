from django import forms
from candidates.models import Offer
from jobs.models import BusinessUnit
from .models import DailyJoining
from django.contrib.auth.models import User


class scheduleForm(forms.Form):
    businessUnit = BusinessUnit.objects.all()
    unitList = [(unit.id, unit.short_name) for unit in businessUnit] 

    unit = forms.ChoiceField(choices=unitList, widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_unit'}))
    from_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="From Date"
    )
    to_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="To Date"
    )
    
    format_ = forms.ChoiceField(choices=[('pdf','PDF'), ('xlsx', 'Excel'), ('docx', 'Word')], widget=forms.Select(attrs={'class': 'form-select'}), label="Format")


class DailyJoiningForm(forms.ModelForm):
    class Meta:
        model = DailyJoining
        fields = ['unit', 'date', 'location','employee_category', 'recruitment_type', 'joinings_count']
        widgets = {
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'employee_category': forms.Select(attrs={'class': 'form-select'}),
            'recruitment_type': forms.Select(attrs={'class': 'form-select'}),
            'joinings_count': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'unit': 'Business Unit',
            'date': 'Date',
            'location': 'Location',
            'employee_category': 'Employee Category',
            'recruitment_type': 'Recruitment Type',
            'joinings_count': 'Joinings Count',
        }
        help_texts = {
            'employee_category': 'Select the Employee Category',
            'recruitment_type': 'Select the Recruitment Type',
            'joinings_count': 'Enter the Joinings Count',
        }
        error_messages = {
            'unit': {'required': 'Business Unit is required'},
            'date': {'required': 'Date is required'},
            'location': {'required': 'Location is required'},
            'employee_category': {'required': 'Employee Category is required'},
            'recruitment_type': {'required': 'Recruitment Type is required'},
            'joinings_count': {'required': 'Joinings Count is required'},
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user.username== "tonmoy.hossain":
            self.fields['location'].initial = "Dhamrai"