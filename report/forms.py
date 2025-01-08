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

        if user.username== "gbml-bagerhat-hr":
            self.fields['location'].initial = "Bagerhat"
        elif user.username== "gbml-bogura-hr":
            self.fields['location'].initial = "Bogura"
        elif user.username== "gbml-jashore-hr":
            self.fields['location'].initial = "Jeshore"
        elif user.username== "gbml-rangpur-hr":
            self.fields['location'].initial = "Rangpur"
        elif user.username== "ppl-pcl-hr":
            self.fields['location'].initial = "Factory"
        elif user.username== "sfll-hr":
            self.fields['location'].initial = "Factory"
        elif user.username== "sorl-hr":
            self.fields['location'].initial = "Factory"
        elif user.username== "svoil-hr":
            self.fields['location'].initial = "Factory"
        elif user.username== "food-comilla-hr":
            self.fields['location'].initial = "Comilla"
        elif user.username== "food-dhamrai-hr":
            self.fields['location'].initial = "Dhamrai"
        elif user.username== "food-gazipur-hr":
            self.fields['location'].initial = "Gazipur"
        elif user.username== "food-narsigdi-hr":
            self.fields['location'].initial = "Narsigndi"
        elif user.username== "food-potiya-hr":
            self.fields['location'].initial = "Potiya"
        else:
            self.fields['location'].initial = "Head Office"