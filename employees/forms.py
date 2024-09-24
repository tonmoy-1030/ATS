from django import forms
from django_select2 import forms as s2forms
from .models import Employee, SeperationStatus, EmployeeConfirmation, TransferOrder, PostingOrder, SalaryInfo
import django_filters


class UploadFileForm(forms.Form):
    file = forms.FileField()
    
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


class SeperationForm(forms.ModelForm):
    class Meta:
        model = SeperationStatus
        fields ='__all__'
        
        widgets = { 
                   'employee' : EmployeeWidgets,
                   'resign_date': forms.DateInput(attrs={'type':'date'}),
                   'reason': forms.TextInput()
                } 
    

class EmployeeEntryForm(forms.ModelForm):
    class Meta:
        model = Employee
        exclude = ['confirmation_date', 'active_status']
        
        widgets = {
            'DOJ' : forms.DateInput(attrs={'type':'date', 'class':'form-control'}),
            'EID': forms.TextInput(attrs={'class':'form-control'}),
            'name': forms.TextInput(attrs={'class':'form-control'})
        }
 
 
class EmployeeFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', label="Name")
    department = django_filters.CharFilter(lookup_expr='icontains', label='Department')
    unit = django_filters.ChoiceFilter(choices=[], label='Unit')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['unit'].extra['choices'] = self.get_unit_choices()

    def get_unit_choices(self):
        unique_units = Employee.objects.values_list('unit__id', 'unit__name').distinct()
        choices = [(unit_id, unit_name) for (unit_id, unit_name) in unique_units]
        return choices
    
    class Meta:
        model = Employee
        fields = ['name', 'department', 'unit']


# employee Confirmation Form
class EmployeeConfirmationForm(forms.ModelForm):
    
    eid = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Enter EID'}), required=True)
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Name'}), required=False)
    
    class Meta:
        model = EmployeeConfirmation
        fields = ['employee', 'new_designation', 'status', 'development_area', 'effective_date', 'remarks']
        widgets = {
            'employee': forms.Select(attrs={"class": 'form-select'}),
            'development_area': forms.Textarea(attrs={"rows": 2}),
            'status': forms.Select(attrs={"class": 'form-select-sm'}),
            'new_designation': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'effective_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control-sm'}),
            'remarks': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
        }
        
class TransferOrderForm(forms.ModelForm):
    
    eid = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter EID','style': 'width: 90.6px; font-size: 12px;' }), required=True)
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control ', 'placeholder': 'Name', 'style': 'width: 160.6px; font-size: 12px; padding-left: 0px; padding-right: 0px'}), required=False)
    
    class Meta:
        model = TransferOrder
        fields = ['employee', 'current_job_location', 'current_location_type', \
                'current_under_region_zone', 'current_under_region_zone_type', 'new_job_location',\
                'new_location_type', 'new_under_region_zone', 'new_under_region_zone_type','new_designation',\
                    'effective_date', 'report_to']
        
        widgets = {
            'employee': forms.Select(attrs={"class": 'form-select'}),
            'current_job_location': forms.TextInput(attrs={"class": 'form-control', 'placeholder': 'Location', 'style': 'font-size: 12px;'}),
            'current_location_type': forms.Select(attrs={"class": 'form-select', 'style': 'width: 70.0px; font-size: 12px;'}),
            'current_under_region_zone': forms.TextInput(attrs={"class": 'form-control', 'style': 'font-size: 12px;'}),
            'current_under_region_zone_type': forms.Select(attrs={"class": 'form-select', 'style': 'width: 70.0px; font-size: 12px;'}),
            'new_job_location': forms.TextInput(attrs={"class": 'form-control', 'style': 'font-size: 12px; width: 95.0px'}),
            'new_location_type': forms.Select(attrs={"class": 'form-select', 'style': 'width: 70.0px; font-size: 12px;'}),
            'new_under_region_zone': forms.TextInput(attrs={"class": 'form-control', 'style': 'font-size: 12px;'}),
            'new_under_region_zone_type': forms.Select(attrs={"class": 'form-select', 'style': 'width: 70.0px; font-size: 12px;'}),
            'new_designation': forms.TextInput(attrs={"class": 'form-control', 'style': 'font-size: 10px; width: 120.6px;'}),
            'report_to': forms.TextInput(attrs={"class": 'form-control', 'style': 'width: 140.0px; font-size: 12px; padding-left: 0px; padding-right: 0px'}),
            'effective_date': forms.DateInput(attrs={'type': 'date',"class": 'form-control', 'style': 'font-size: 12px;'}),            
        }
        
class PostingOrderForm(forms.ModelForm):
    
    eid = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter EID','style': 'width: 90.6px; font-size: 12px;' }), required=True)
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control ', 'placeholder': 'Name', 'style': 'width: 180.6px; font-size: 12px; padding-left: 0px; padding-right: 0px'}), required=False)
    
    class Meta:
        model = PostingOrder
        fields = ['employee', 'new_job_location', 'new_location_type', 'new_under_region_zone', \
                'new_under_region_zone_type', 'effective_date', 'report_to']
        
        widgets = {
            'employee': forms.Select(attrs={"class": 'form-select'}),
            'new_job_location': forms.TextInput(attrs={"class": 'form-control', 'style': 'font-size: 12px;'}),
            'new_location_type': forms.Select(attrs={"class": 'form-select', 'style': 'width: 95.0px; font-size: 12px;'}),
            'new_under_region_zone': forms.TextInput(attrs={"class": 'form-control', 'style': 'font-size: 12px;'}),
            'new_under_region_zone_type': forms.Select(attrs={"class": 'form-select', 'style': 'width: 95.0px; font-size: 12px;'}),
            'report_to': forms.TextInput(attrs={"class": 'form-control', 'style': 'width: 180.0px; font-size: 12px; padding-left: 0px; padding-right: 0px'}),
            'effective_date': forms.DateInput(attrs={'type': 'date',"class": 'form-control', 'style': 'font-size: 12px;'}),
            
            
        }

class SalaryInfoForm(forms.ModelForm):
    
    class Meta:
        model = SalaryInfo
        fields = ['employee','salary', 'report_to', 'place_of_posting','director_signature', 
                  'CC1', 'CC2', 'CC3', 'CC4', 'CC5', 'CC6', 'CC6','CC7' ]
        
        widgets = {
            'employee': EmployeeWidgets,
            'salary': forms.NumberInput(attrs={'class':'form-control'})
        }

