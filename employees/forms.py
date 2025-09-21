from django import forms
from django_select2 import forms as s2forms
from .models import Employee, SeperationStatus, EmployeeConfirmation, TransferOrder, PostingOrder, SalaryInfo, OfficialDocument, SalesOfficerLocation
import django_filters
from django.db.models import Q

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
            'name': forms.TextInput(attrs={'class':'form-control'}),
            'personal_file': forms.ClearableFileInput(attrs={'class':'form-control'})
        }
 
 
class EmployeeFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(
        method='filter_search', 
        label='Search'
    )
    unit = django_filters.ChoiceFilter(choices=[], field_name='unit__id', label='Unit')

    def filter_search(self, queryset, name, value):
        """
        Custom filter: search 'value' in name, EID, or designation
        """
        return queryset.filter(
            Q(name__icontains=value) |
            Q(EID__icontains=value) |
            Q(designation__icontains=value) |
            Q(mobile_no_icontains=value) 
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['unit'].extra['choices'] = self.get_unit_choices()

    def get_unit_choices(self):
        unique_units = Employee.objects.values_list('unit__id', 'unit__name').distinct()
        choices = [(unit_id, unit_name) for (unit_id, unit_name) in unique_units]
        return choices

    class Meta:
        model = Employee
        fields = ['search', 'unit']
    
class SeparationFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='employee__name',lookup_expr='icontains', label="Name")
    resignation_date = django_filters.DateFromToRangeFilter(field_name='resign_date', label='Resign Date', widget=django_filters.widgets.RangeWidget(
                                                    attrs={'type': 'date'}
                                                    ))
    unit = django_filters.ChoiceFilter(field_name='employee__unit', choices=[], label='Unit')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['unit'].extra['choices'] = self.get_unit_choices()

    def get_unit_choices(self):
        unique_units = Employee.objects.values_list('unit__id', 'unit__name').distinct()
        choices = [(unit_id, unit_name) for (unit_id, unit_name) in unique_units]
        return choices
    
    class Meta:
        model = SeperationStatus
        fields = ['name', 'resignation_date', 'unit']
        

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

class TransferOrderUpdateForm(forms.ModelForm):
    
    class Meta:
        model = TransferOrder
        fields = ['employee', 'current_job_location', 'current_location_type', 'current_under_region_zone', 'current_under_region_zone_type',\
            'new_job_location', 'new_location_type', 'new_under_region_zone', 'new_under_region_zone_type', 'new_designation', 'report_to', 'effective_date']   

        widgets = {
            'employee': EmployeeWidgets,
            'current_job_location': forms.TextInput(attrs={"class": 'form-control', 'placeholder': 'Location', 'label':'Current Location'}),
            'current_location_type': forms.Select(attrs={"class": 'form-select'}),
            'current_under_region_zone': forms.TextInput(attrs={"class": 'form-control'}),
            'current_under_region_zone_type': forms.Select(attrs={"class": 'form-select'}),
            'new_job_location': forms.TextInput(attrs={"class": 'form-control'}),
            'new_location_type': forms.Select(attrs={"class": 'form-select'}),
            'new_under_region_zone': forms.TextInput(attrs={"class": 'form-control'}),
            'new_under_region_zone_type': forms.Select(attrs={"class": 'form-select'}),
            'new_designation': forms.TextInput(attrs={"class": 'form-control'}),
            'report_to': forms.TextInput(attrs={"class": 'form-control'}),
            'effective_date': forms.DateInput(attrs={'type': 'date'}), 
        }
        labels ={
            'current_job_location':'Current Location',
            'current_location_type':'Type',
            'current_under_region_zone':'Region/Zone',
            'current_under_region_zone_type':'Type',
            'new_job_location':'New Location',
            'new_location_type':'Type',
            'new_under_region_zone':'New Region/Zone',
            'new_under_region_zone_type':'Type'            
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
        
class PostingOrderUpdateForm(forms.ModelForm):
    
    class Meta:
        model = PostingOrder
        fields = ['employee', 'new_job_location', 'new_location_type', 'new_under_region_zone', 'new_under_region_zone_type', 'report_to', 'effective_date']   

        widgets = {
            'employee': EmployeeWidgets,
            'new_job_location': forms.TextInput(attrs={"class": 'form-control'}),
            'new_location_type': forms.Select(attrs={"class": 'form-select'}),
            'new_under_region_zone': forms.TextInput(attrs={"class": 'form-control'}),
            'new_under_region_zone_type': forms.Select(attrs={"class": 'form-select'}),
            'report_to': forms.TextInput(attrs={"class": 'form-control'}),
            'effective_date': forms.DateInput(attrs={'type': 'date'}), 
        }
        labels ={
            'new_job_location':'New Location',
            'new_location_type':'Type',
            'new_under_region_zone':'New Region/Zone',
            'new_under_region_zone_type':'Type'            
        }

class SalaryInfoForm(forms.ModelForm):
    
    class Meta:
        model = SalaryInfo
        fields = ['employee','salary', 'report_to', 'place_of_posting','notice_period','director_signature', 
                  'CC1', 'CC2', 'CC3', 'CC4', 'CC5', 'CC6', 'CC6','CC7' ]
        
        widgets = {
            'employee': EmployeeWidgets,
            'salary': forms.NumberInput(attrs={'class':'form-control'})
        }



class OfficialDocumentForm(forms.ModelForm):
    class Meta:
        model = OfficialDocument
        fields = ['employee', 'document_type', 'issue_date', 'reason', 'remarks', 'document']
        widgets = {
            'employee': EmployeeWidgets,
            'document_type': forms.TextInput(attrs={'class': 'form-control'}),
            'issue_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'reason': forms.TextInput(attrs={'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'document': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'
            })
        }
        labels = {
            'employee': 'Select Employee',
            'document_type': 'Document Type',
            'issue_date': 'Issue Date',
            'reason': 'Reason',
            'document': 'Upload Document',
            'remarks': 'Remarks'
        }

    def clean_document(self):
        document = self.cleaned_data.get('document')
        if document:
            # Get the file extension
            ext = document.name.split('.')[-1].lower()
            # Define allowed file types
            allowed_types = ['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png']
            if ext not in allowed_types:
                raise forms.ValidationError('Only PDF, Word documents and images (JPG, PNG) are allowed.')
            # Check file size (max 5MB)
            if document.size > 5 * 1024 * 1024:
                raise forms.ValidationError('File size must be no more than 5MB.')
        return document
    

salesOfficerInfoFormset = forms.inlineformset_factory(
    Employee, SalaryInfo, fields=['salary',], extra=1, can_delete=False
)

salesOfficerLocationFormset = forms.inlineformset_factory(
    Employee,
    SalesOfficerLocation,
    fields=['area', 'region', 'zone', 'distributor_name'],
    extra=1,
    can_delete=False
)