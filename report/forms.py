from django import forms
from candidates.models import Offer
from jobs.models import BusinessUnit


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
