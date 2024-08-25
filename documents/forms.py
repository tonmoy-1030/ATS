import django_filters
import django_filters.widgets
from employees.models import Employee, EmployeeConfirmation, TransferOrder, PostingOrder, SalaryInfo
from django_select2 import forms as s2forms
from django import forms



class EmployeeFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    unit = django_filters.ChoiceFilter(choices=[])
    from_doj = django_filters.DateFromToRangeFilter(field_name='DOJ',
                                                    widget=django_filters.widgets.RangeWidget(
                                                    attrs={
                                                            'type': 'date'
                                                        }
                                                    )
                                                )  

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['unit'].extra['choices'] = self.get_unit_choices()

    def get_unit_choices(self):
        unique_units = Employee.objects.values_list('unit', flat=True).distinct()
        choices = [(unit, unit) for unit in unique_units]
        return choices

    class Meta:
        model = Employee
        fields = ['name', 'unit', 'from_doj']
        

class EmployeeConfirmationFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name')
    unit = django_filters.ChoiceFilter(choices=[])

    confirmation_date = django_filters.DateFromToRangeFilter(field_name='confirmation_date',
                                                    widget=django_filters.widgets.RangeWidget(
                                                    attrs={
                                                            'type': 'date'
                                                        }
                                                    )
                                                )  
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['unit'].extra['choices'] = self.get_unit_choices()

    def get_unit_choices(self):
        unique_units = Employee.objects.values_list('unit', flat=True).distinct()
        choices = [(unit, unit) for unit in unique_units]
        return choices


    class Meta:
        model = Employee
        fields = ['name', 'unit', 'confirmation_date']
        
class EmployeeConfirmationLetterFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='employee__name')
    unit = django_filters.ChoiceFilter(field_name='employee__unit', choices=[])

    issue_date = django_filters.DateFromToRangeFilter(field_name='issue_date',
                                                    widget=django_filters.widgets.RangeWidget(
                                                    attrs={
                                                            'type': 'date',
                                                        }
                                                    )
                                                )  
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['unit'].extra['choices'] = self.get_unit_choices()

    def get_unit_choices(self):
        unique_units = Employee.objects.values_list('unit', flat=True).distinct()
        choices = [(unit, unit) for unit in unique_units]
        return choices


    class Meta:
        model = EmployeeConfirmation
        fields = ['name', 'unit', 'issue_date']

class TransferLetterFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='employee__name')
    unit = django_filters.ChoiceFilter(field_name='employee__unit', choices=[])

    issue_date = django_filters.DateFromToRangeFilter(field_name='issue_date',
                                                    widget=django_filters.widgets.RangeWidget(
                                                    attrs={
                                                            'type': 'date'
                                                        }
                                                    )
                                                )  
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['unit'].extra['choices'] = self.get_unit_choices()

    def get_unit_choices(self):
        unique_units = Employee.objects.values_list('unit', flat=True).distinct()
        choices = [(unit, unit) for unit in unique_units]
        return choices


    class Meta:
        model = TransferOrder
        fields = ['name', 'unit', 'issue_date']

class PostingLetterFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='employee__name')
    unit = django_filters.ChoiceFilter(field_name='employee__unit', choices=[])

    issue_date = django_filters.DateFromToRangeFilter(field_name='issue_date',
                                                    widget=django_filters.widgets.RangeWidget(
                                                    attrs={
                                                            'type': 'date'
                                                        }
                                                    )
                                                )  
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['unit'].extra['choices'] = self.get_unit_choices()

    def get_unit_choices(self):
        unique_units = Employee.objects.values_list('unit', flat=True).distinct()
        choices = [(unit, unit) for unit in unique_units]
        return choices


    class Meta:
        model = PostingOrder
        fields = ['name', 'unit', 'issue_date']

    
class AppointmentLetterFilter(django_filters.FilterSet):
    
    name = django_filters.CharFilter(field_name= 'employee__name' ,lookup_expr='icontains', label="Name")
    issue_date = django_filters.DateFromToRangeFilter(field_name='issue_date', label="Issue Date",
                                                    widget=django_filters.widgets.RangeWidget(
                                                    attrs={'type': 'date'}
                                                    )
                                                )    
    
    unit = django_filters.ChoiceFilter(field_name="employee__unit", choices=[], label='Unit')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['unit'].extra['choices'] = self.get_unit_choices()

    def get_unit_choices(self):
        unique_units = Employee.objects.values_list('unit', flat=True).distinct()
        choices = [(unit, unit) for unit in unique_units]
        return choices
    
    class Meta:
        model = SalaryInfo
        fields = ['name', 'unit','issue_date' ]
        

class CandidateDetailsForm(forms.Form):
    BUSINESS_UNIT = [
        ('Consumer Division', 'Consumer'),
        ('T.K. Food Products Distribution Limited', 'T.K. Food'),
        ('Prime Pusti Limited', 'PPL'),
        ('Prime Cosmetics Limited', 'PCL'),
        ('Pusti Glory', 'Glory'),
    ]
    unit = forms.MultipleChoiceField(choices=BUSINESS_UNIT, widget=forms.SelectMultiple(attrs={'class': 'form-select', 'id': 'id_unit'}))
    from_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="From Date"
    )
    to_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="To Date"
    )
    