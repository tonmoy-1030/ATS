from typing import Any
from django import forms
import django_filters.widgets
from django_select2 import forms as s2forms
from employees.models import Employee
from .models import LeaveAllocation, LeaveApplication, Holiday
import django_filters
from django.core.exceptions import ValidationError


# Employee Select2      
class EmployeeWidgets(s2forms.ModelSelect2Widget):
    model = Employee
    search_fields =[
        'EID__icontains',
        'name__icontains',
        'unit__name__icontains',
    ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs['data-placeholder'] ='Select Employee.......'
        self.attrs['data-minimum-input-length'] = 0
        self.attrs['class'] = 'form-select'

# Allocation Form
class LeaveAllocationForm(forms.ModelForm):
    
    class Meta:
        model = LeaveAllocation
        fields = ['employee', 'leave_type', 'year', 'leave_allocated', 'leave_taken', 'leave_balance']
        widgets = {
            'employee': EmployeeWidgets,
            'leave_type': forms.Select(attrs={'class':'form-select'}),
            'year':forms.NumberInput(attrs={'class':'form-control'}),
            'leave_allocated':forms.NumberInput(attrs={'class':'form-control'}),
            'leave_taken':forms.NumberInput(attrs={'class':'form-control'}),
            'leave_balance':forms.NumberInput(attrs={'class':'form-control', 'readonly': 'readonly'})
        }

# Application Form
class LeaveApplicationForm(forms.ModelForm):
    
    class Meta:
        model = LeaveApplication
        fields = ['employee', 'leave_type', 'start_date', 'end_date', 'total_days', 'remarks']
        
        
        widgets = {
            'employee': EmployeeWidgets,
            'leave_type': forms.Select(attrs={'class':'form-select'}),
            'start_date':forms.DateInput(attrs={'class':'form-control', 'type': 'date'}),
            'end_date':forms.DateInput(attrs={'class':'form-control', 'type': 'date'}),
            'total_days': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'remarks':forms.TextInput(attrs={'class':'form-control'})
        }



# Holiday form
class HolidayForm(forms.ModelForm):
    
    class Meta:
        model = Holiday
        fields = "__all__"
        widgets = {
            'date': forms.DateInput(attrs={'class':'form-control', 'type':'date'}),
            'name': forms.TextInput(attrs={'class':'form-control'})
        }
            
    
# Leave Filter Form
class LeaveFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="employee__name", lookup_expr="icontains", label="Name",  widget=forms.TextInput(attrs={'class': 'form-control'}))
    department = django_filters.CharFilter(field_name="employee__department", lookup_expr="icontains", label="Department", widget=forms.TextInput(attrs={'class': 'form-control'}))
    unit = django_filters.ChoiceFilter(field_name="employee__unit",choices=[], label="Unit", widget=forms.Select(attrs={'class': 'form-select'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['unit'].extra['choices'] = self.get_unit_choices()

    def get_unit_choices(self):
        unique_units = Employee.objects.values_list('unit__id','unit__name').distinct()
        choices = [(unit_id, unit_name) for (unit_id, unit_name) in unique_units]
        return choices
    
    class Meta:
        model = LeaveApplication
        fields = ['name', 'department', 'unit'] 


# Allocation Filter Form
class LeaveAllocationFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="employee__name", lookup_expr="icontains", label="Name",  widget=forms.TextInput(attrs={'class': 'form-control'}))
    department = django_filters.CharFilter(field_name="employee__department", lookup_expr="icontains", label="Department", widget=forms.TextInput(attrs={'class': 'form-control'}))
    unit = django_filters.ChoiceFilter(field_name="employee__unit",choices=[], label="Unit", widget=forms.Select(attrs={'class': 'form-select'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['unit'].extra['choices'] = self.get_unit_choices()

    def get_unit_choices(self):
        unique_units = Employee.objects.values_list('unit__id','unit__name').distinct()
        choices = [(unit_id, unit_name) for (unit_id, unit_name) in unique_units]
        return choices
    
    class Meta:
        model = LeaveAllocation
        fields = ['name', 'department', 'unit'] 

# Holiday Filter Form        
class HolidayFilter(django_filters.FilterSet):
    year = django_filters.ChoiceFilter(
        field_name="date",
        label="Year",
        method='filter_by_year',
        choices=[],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['year'].extra['choices'] = self.get_year_choices()

    def get_year_choices(self):
        # Extract unique years from the date field
        unique_years = Holiday.objects.dates('date', 'year', order='DESC')
        choices = [(year.year, year.year) for year in unique_years]
        return choices

    def filter_by_year(self, queryset, name, value):
        if value:
            queryset = queryset.filter(date__year=value)
        return queryset

    class Meta:
        model = Holiday
        fields = ['year']

class UploadFileForm(forms.Form):
    file = forms.FileField()