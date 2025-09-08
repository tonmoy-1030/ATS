from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse,JsonResponse
from django.urls import reverse
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from .models import (Employee, SeperationStatus, 
                     EmployeeDetails,EmployeeConfirmation,
                     TransferOrder, PostingOrder, SalaryInfo, OfficialDocument)
from .forms import (UploadFileForm, SeperationForm, 
                    EmployeeEntryForm, EmployeeFilter, 
                    TransferOrderForm, EmployeeConfirmationForm, 
                    PostingOrderForm, SalaryInfoForm, TransferOrderUpdateForm,
                    PostingOrderUpdateForm, SeparationFilter, OfficialDocumentForm, 
                    salesOfficerInfoFormset, salesOfficerLocationFormset)
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from datetime import datetime, timedelta
import csv, os, re
from django.conf import settings
from django.db import IntegrityError
from candidates.models import Candidate
from .utils.google_form_Employees import NewEmployeeData
from django.contrib import messages
from django.forms import modelformset_factory
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.utils import timezone
from jobs.models import BusinessUnit
import requests
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image
from django.core.cache import cache
from .tasks import update_sales_officer_joining_date_task


class EmployeeListView(ListView):
    model = Employee
    paginate_by = 12
    template_name = 'employees/employees.html'
    context_object_name = 'employee_list'
    
    
    def get_queryset(self):
        queryset = super().get_queryset()
        filter = EmployeeFilter(self.request.GET, queryset=Employee.objects.all())
        return filter.qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = EmployeeFilter(self.request.GET, queryset=self.get_queryset())
        return context
    
   

def import_employees(file):
    temp_directory = os.path.join(settings.MEDIA_ROOT, 'temp')
    os.makedirs(temp_directory, exist_ok=True)

    temp_file_path = os.path.join(temp_directory, file.name)
    with open(temp_file_path, 'wb') as temp_file:
        for chunk in file.chunks():
            temp_file.write(chunk)
            
    with open(temp_file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            print(row)
            try:
                DOJ_str = row['DOJ']
                DOJ = datetime.strptime(DOJ_str, '%Y-%m-%d').date()
            except ValueError:
                return HttpResponse("Please reformat date of joining like YYYY-MM-DD")

            try:
                employee, created = Employee.objects.update_or_create(
                    EID=row['EID'],
                    defaults={
                        'name': row['Name'],
                        'designation': row['Designation'],
                        'department': row['Department'],
                        'DOJ': DOJ,
                        'mobile_no': row['Mobile_no'],
                        'email': row['Email'],
                        'unit': BusinessUnit.objects.filter(id=row['Unit']).first()
                    }
                )
                # If the employee already exists, update the existing record
                if not created:
                    employee.name = row['Name']
                    employee.designation = row['Designation']
                    employee.department = row['Department']
                    employee.DOJ = DOJ
                    employee.mobile_no = row['Mobile_no']
                    employee.email = row['Email']
                    employee.unit = BusinessUnit.objects.filter(id=row['Unit']).first()
                    employee.save()
            except IntegrityError:
                return HttpResponse("Please check the CSV file again")
        


class EmployeeCreateView(SuccessMessageMixin, CreateView):
    model = Employee
    form_class = EmployeeEntryForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        business_unit = BusinessUnit.objects.all()
        context['business_units'] = business_unit
        return context
    
    def get_success_url(self):
        return reverse('employees:employee-create')
    success_message = "Employee Entered Successfully"
    
    
class EmployeeUpdateView(SuccessMessageMixin, UpdateView):
    model = Employee
    template_name = 'employees/employee_update_form.html'
    form_class = EmployeeEntryForm
    
    def get_success_url(self):
        return reverse('employees:employee')
    success_message = "Employee information updated Successfully"



def determine_pattern(unit):
    if unit == 'Prime Pusti Limited':
        return 'PPL-P{0:03d}'
    elif unit == 'Prime Cosmetics Limited':
        return 'PCL-P{0:03d}'
    elif unit == 'T.K. Logistics':
        return 'TKL{0:03d}'
    else:
        return '0{0}'

def get_candidate_data(request):
    candidate_id = request.GET.get('candidate_id')
    candidate = Candidate.objects.get(pk=candidate_id)

    exclude_patterns = ['02214', 'PC ', '02201', '02206', '02000', '02214', 'PCL-C', 'PPL-C', 'PG', 'TKFS', 'EMP', '0340']
    exclude_condition = Q()
    for pattern in exclude_patterns:
        exclude_condition |= Q(EID__startswith=pattern)
        
    matching_eids = Employee.objects.filter(unit=candidate.offer.job.unit)\
                                     .exclude(exclude_condition)\
                                     .values_list('EID', flat=True)

    numeric_parts = []
    for eid in matching_eids:
        numeric_part_match = re.search(r'\d+$', eid)
        if numeric_part_match:
            numeric_parts.append(int(numeric_part_match.group()))

    # Use a default value (0) if no numeric part was found, so the new EID starts with 1.
    if numeric_parts:
        max_numeric_part = max(numeric_parts)
    else:
        max_numeric_part = 0

    unit_pattern = determine_pattern(candidate.offer.job.unit.name)
    new_eid = unit_pattern.format(max_numeric_part + 1)

    data = {
        'EID': new_eid,
        'name': candidate.name,
        'designation': candidate.offer.offered_designation,
        'department': candidate.offer.job.department,
        'email': candidate.email,
        'DOJ': candidate.offer.joining_date.strftime('%Y-%m-%d'),
        'personal_cell': candidate.mobile,
        'unit': candidate.offer.job.unit.id,
        'job': candidate.offer.job.id,
        'candidate': candidate.pk,
    }
    return JsonResponse(data)
    
def upload_file(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            import_employees(request.FILES["file"])
            return HttpResponseRedirect("/employees")
    else:
        form = UploadFileForm()
    return render(request, "employees/upload.html", {"form": form})
    

def sample_employee_upload_file(request):
    response = HttpResponse(
        content_type='text/csv',
        headers = {"Content-Dispositon": "'attachment; 'filename'='sample.csv'"}
    )  
    writter = csv.writer(response)
    header_row = ['EID','Name','Designation','Department','DOJ', 'Mobile_no','Email','Unit']  
    writter.writerow(header_row)
    row = ['2000006','Md. Ashraful Hossain Nury','Manager', 'Brand','2005-01-03','0','test@tkgroupbd.com', 'unit_ID']
    writter.writerow(row)
    
    return response


class EmployeeDeleteView(DeleteView):
    model = Employee
    template_name = 'employees/employees.html'
    context_object_name = 'employee_list'
    success_url = "/employees"

class EmployeeSeparationCreateView(CreateView, SuccessMessageMixin):
    model = SeperationStatus
    form_class = SeperationForm
    template_name = "employees/seperation_form.html"
    success_url = "/employees/separation"
    success_message = "Employee Separation Status Entered Successfully"
    
class EmployeeSeperationUpdateView(UpdateView, SuccessMessageMixin):
    model = SeperationStatus
    form_class = SeperationForm
    template_name = "employees/seperation_form.html"
    success_url = "/employees/separation"
    success_message = "Employee Separation Status updated Successfully"

class EmployeeSeparationListView(ListView):
    model = SeperationStatus
    paginate_by = 12
    template_name = 'employees/Separated_employees.html'
    context_object_name = 'Separated_employees'
    
    
    def get_queryset(self):
        queryset = super().get_queryset()
        filter = SeparationFilter(self.request.GET, queryset=SeperationStatus.objects.all().order_by('-resign_date'))
        return filter.qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = SeparationFilter(self.request.GET, queryset=self.get_queryset())
        return context
    


def sample_separated_upload_file(request):
    response = HttpResponse(
        content_type='text/csv',
        headers = {"Content-Dispositon": "'attachment; 'filename'='sample_separation.csv'"}
    )  
    writter = csv.writer(response)
    header_row = ['EID','Name', 'Resign_Date', 'Reason']  
    writter.writerow(header_row)
    row = ['2000006','Md. Ashraful Hossain Nury', '2021-01-03', 'Personal Reason']
    writter.writerow(row)
    
    return response


def import_separated_employees(file):
    temp_directory = os.path.join(settings.MEDIA_ROOT, 'temp')
    os.makedirs(temp_directory, exist_ok=True)

    temp_file_path = os.path.join(temp_directory, file.name)
    with open(temp_file_path, 'wb') as temp_file:
        for chunk in file.chunks():
            temp_file.write(chunk)

    with open(temp_file_path, 'r') as temp_file:
        reader = csv.DictReader(temp_file)
        error_messages = []
        for row in reader:
            try:
                resign_date_str = row['Resign_Date']
                resign_date = datetime.strptime(resign_date_str, '%Y-%m-%d').date()
            except ValueError:
                error_messages.append(f"Invalid date format for ID {row['EID']}: {resign_date_str}")
                continue
            
            try:
                employee = Employee.objects.get(EID=row['EID'])
            except Employee.DoesNotExist:
                error_messages.append(f"Employee with ID {row['EID']} does not exist")
                continue

            try:
                employee, created = SeperationStatus.objects.update_or_create(
                    employee=employee,
                    defaults={
                    "resign_date":resign_date,
                    "reason":row['Reason']
                    }
                )
                
                if not created:
                    employee.resign_date = resign_date
                    employee.reason = row['Reason']
                    
            except Exception as e:
                error_messages.append(f"Error creating SeperationStatus for ID {row['ID']}: {str(e)}")
        
        if error_messages:
            return HttpResponse("<br>".join(error_messages))
    
    os.remove(temp_file_path)                    
        
def separate_upload_file(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            response = import_separated_employees(request.FILES["file"])
            if response:
                return response
            return HttpResponseRedirect("/employees/")
    else:
        form = UploadFileForm()
    return render(request, "employees/upload_separation.html", {"form": form})


#update Employee Details
def employee_details(request):
    alert_messages = []
    employees_data = NewEmployeeData().get_employee_data()
    if employees_data:
        for key, details in employees_data.items():
            try:
                mobile_no = key
                employee = Employee.objects.filter(mobile_no=mobile_no).last()
                if employee:
                    if not hasattr(employee, 'details'):
                        EmployeeDetails.objects.create(employee=employee)

                    employee.details.official_mobile = ""
                    employee.details.emergency_contact_person = details.get("Emergency Contact Person Name", "").title()
                    employee.details.emergency_contact_no = details.get("Emergency Contact No", "")
                    employee.details.emergency_person_address = details.get("Address", "")
                    employee.details.emer_relation_with_employee = details.get('Relation with Employee', "")
                    employee.details.present_vill = employee.candidate.details.present_vill.title()
                    employee.details.present_po = employee.candidate.details.present_po.title()
                    employee.details.present_ps = employee.candidate.details.present_ps.title()
                    employee.details.present_dist = employee.candidate.details.present_dist.title()
                    employee.details.permanent_vill = employee.candidate.details.permanent_vill.title()
                    employee.details.permanent_po = employee.candidate.details.permanent_po.title()
                    employee.details.permanent_ps = employee.candidate.details.permanent_ps.title()
                    employee.details.permanent_dist = employee.candidate.details.permanent_dist.title()
                    employee.details.date_of_birth = employee.candidate.details.date_of_birth
                    employee.details.blood_group = employee.candidate.details.blood_group
                    employee.details.father_name = details.get("Father's Name", "").title()
                    employee.details.mother_name = details.get("Mother's Name", "").title()
                    employee.details.nid = employee.candidate.details.nid
                    employee.details.tin = details.get("Tax Identification Number (TIN)", "")
                    employee.details.marital_status = details.get("Marital Status", "")
                    employee.details.spouse_name = details.get("Spouse Name", "").title()
                    employee.details.no_of_son = details.get("Number of Son", 0)
                    employee.details.no_of_daughter = details.get("Number of Daughter", 0)
                    employee.details.highest_degree = employee.candidate.details.degree_name
                    employee.details.subject_highest_degree = employee.candidate.details.subject_highest_degree
                    employee.details.institution_highest_degree = employee.candidate.details.institution_highest_degree.title()
                    employee.details.passing_year_highest_degree = employee.candidate.details.passing_year_highest_degree
                    employee.details.division_or_gpa_highest_degree = employee.candidate.details.division_or_gpa_highest_degree
                    employee.details.professional_degree = employee.candidate.details.professional_degree
                    employee.details.subject_professional_degree = employee.candidate.details.subject_professional_degree
                    employee.details.institution_professional_degree = employee.candidate.details.institution_professional_degree 
                    employee.details.passing_year_professional_degree = employee.candidate.details.passing_year_professional_degree
                    employee.details.nominee_name = details.get("Nominee's Name", "").title()
                    employee.details.nominee_father_name = details.get("Nominee's Father's Name", "").title()
                    employee.details.nominee_mohter_name = details.get("Nominee's Mother's Name", "").title()
                    employee.details.nominee_mobile_no = details.get("Nominee's Mobile Number", "")
                    employee.details.relation_with_employee = details.get("Relationship with Employee", "").title()
                    employee.details.nominee_nid = details.get("Nominee's NID", "")
                    employee.details.nominee_vill = details.get("Village", "").title()
                    employee.details.nominee_po = details.get("Post Office", "").title()
                    employee.details.nominee_ps = details.get("Police Station", "").title()
                    employee.details.nominee_dist = details.get("District", "").title()
                    employee.details.religion = employee.candidate.details.religion.title()
                   
                    
                    file_id = details.get('Upload Your Passport Size Photo(Formal Photo)', "").split('id=')[-1]
                    file_url =  f'https://drive.usercontent.google.com/download?id={file_id}'

                   
                    employee.details.profile_picture = file_url

                    if not employee.details.profile_image:
                        response = requests.get(file_url, stream=True)
                        content_type = response.headers.get("Content-Type", "")
                        
                        if response.status_code == 200 and "image" in content_type:
                            try:
                                # Open image from response
                                img = Image.open(BytesIO(response.content))
                                img_format = img.format.lower()  # jpg, png, etc.
                                
                                # Save directly to Django ImageField
                                image_io = BytesIO()
                                img.save(image_io, format=img.format)
                                image_name = f"{employee.EID}-{employee.name}.{img_format}"
                                
                                employee.details.profile_image.save(
                                    image_name, ContentFile(image_io.getvalue()), save=True
                                )
                                print(f"✅ Saved image for {employee.name}")
                                
                            except Exception as e:
                                print(f"❌ Error decoding image for {employee.name}: {e}")
                        else:
                            print(f"❌ {employee.name} - Failed to retrieve image, status code: {response.status_code}, content-type: {content_type}")

                    employee.email = employee.candidate.email
                    employee.save()
                    
                    employee.details.save()
                    
                    # alert_messages.append(f"Employee details for {mobile_no} updated successfully.")
                else:
                    alert_messages.append(f"Employee with mobile number {mobile_no, details.get("Name")} not found.")
            except Employee.DoesNotExist:
                alert_messages.append(f"Employee with mobile number {mobile_no, details.get("Name")} not found.")
            except Exception as e:
                alert_messages.append(f"Error processing details for {mobile_no, details.get("Name")}: {e}")
    else:
        alert_messages.append("Details do not exist.")
        
    if not alert_messages:
        alert_messages.append("All employee details updated successfully.")
    
    return JsonResponse({'alert_messages': alert_messages}, safe=False)



def employee_confirmation(request):
    EmployeeConfirmationFormSet = modelformset_factory(EmployeeConfirmation, form=EmployeeConfirmationForm, extra=1)
    
    if request.method == 'POST':
        formset = EmployeeConfirmationFormSet(request.POST)
        if formset.is_valid():
            formset.save()
            messages.success(request, "Data Save Successfully")
            return redirect('employees:employee-confirmation')
    else:
        initial_data = [{'development_area': "However, you are advised to improve upon on the areas of "}]
        formset = EmployeeConfirmationFormSet(queryset=EmployeeConfirmation.objects.none(), initial=initial_data)

    return render(request, 'employees/confirmation.html', {'formset': formset})




def employee_search(request):
    term = request.GET.get('eid', "")
    try:
        employee = Employee.objects.get(EID=term)
        results = {
            'id': employee.EID,
            'name': employee.name,
            'employee': employee.id,
            'designation': employee.designation,
        }
    except Employee.DoesNotExist:
        results = {}

    return JsonResponse({'results': results})


def transfer_order(request):
    TransferFormset = modelformset_factory(TransferOrder, TransferOrderForm, extra=10)
    if request.method == "POST":
        formset = TransferFormset(request.POST)
        if formset.is_valid:
            formset.save()
            messages.success(request, "Data Save Successfully")
            return redirect("employees:employee-transfer")
    else:
        formset = TransferFormset(queryset=TransferOrder.objects.none())
        
    return render(request, 'employees/transfer_order.html', {'formset':formset})

class TransferUpdateView(UpdateView, SuccessMessageMixin):
    model = TransferOrder
    template_name="employees/transferForm.html"
    form_class = TransferOrderUpdateForm
    success_message = "Transfer Order Updated Successfully"
    success_url = "/employee/transfer_order_list/"

class PostingUpdateView(UpdateView, SuccessMessageMixin):
    model = PostingOrder
    template_name="employees/postingForm.html"
    form_class = PostingOrderUpdateForm
    success_message = "Posting Order Updated Successfully"
    success_url = "/employee/posting_order_list/"

def posting_order(request):
    PostingFormset = modelformset_factory(PostingOrder, PostingOrderForm, extra=10)
    if request.method == "POST":
        formset = PostingFormset(request.POST)
        if formset.is_valid:
            formset.save()
            messages.success(request, "Data Save Successfully")
            return redirect("employees:employee-posting")
    else:
        formset = PostingFormset(queryset=PostingOrder.objects.none())
        
    return render(request, 'employees/posting_order.html', {'formset':formset})

class EmployeeProfile(DetailView):
    model = Employee
    template_name = "employees/employee_profile.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employees'] = Employee.objects.all()
        return context
    

# Employee List for Appointment Letter   
class EmployeeSalaryInfo(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = SalaryInfo
    form_class = SalaryInfoForm
    template_name = "employees/salary_info.html"
    
    login_url= '/accounts/login'
    redirect_field_name = 'next'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_success_url(self):
        return reverse("employees:salary_info")
    
    
def unit_based_employee_search(request):
     
    try:
        term = request.GET.get('unit_id', "")
        offered_candidates = Candidate.objects.filter(
        offer__job__unit__id=term,
        offer__offer_status='Accepted'
        ).exclude(
            employee__isnull=False
        ).exclude(
            offer__joining_date__lte=timezone.now().date() - timedelta(days=2)
        )

        results = [{'id': candidate.id, 'name': candidate.name} for candidate in offered_candidates]
        results = results
    except:
        results = {}

    return JsonResponse({'results': results})


class OfficialDocumentCreateView(SuccessMessageMixin, CreateView):
    model = OfficialDocument
    form_class = OfficialDocumentForm  # ✅ use the form, not the model
    template_name = "employees/official_document.html"
    success_message = "Official Document Created Successfully"

    def get_success_url(self):
        return reverse("employees:employee_documents")    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get('q', '')
        if search_query:
            context['documents'] = OfficialDocument.objects.filter(
                Q(employee__name__icontains=search_query) |
                Q(employee__EID__icontains=search_query) |
                Q(document_type__icontains=search_query) |
                Q(employee__department__icontains=search_query) |
                Q(employee__designation__icontains=search_query)
            ).select_related('employee').order_by('-uploaded_at')
        else:
            context['documents'] = OfficialDocument.objects.all().select_related('employee').order_by('-uploaded_at')
        context['search_query'] = search_query
        return context


class OfficialDocumentUpdateView(SuccessMessageMixin, UpdateView):
    model = OfficialDocument
    form_class = OfficialDocumentForm  # ✅ use the form, not the model
    template_name = "employees/official_document.html"
    success_message = "Official Document Updated Successfully"

    def get_success_url(self):
        return reverse("employees:employee_documents")
    
class OfficialDocumentDeleteView(SuccessMessageMixin, DeleteView):
    model = OfficialDocument
    success_message = "Official Document Deleted Successfully"

    def get_success_url(self):
        return reverse("employees:employee_documents")

def Sales_Officer_Google_Sheet(request):
    unit_id = request.GET.get('unit_id', "")
    cache_key = f"sales_officer_data_{unit_id}"

    # Try Redis cache first
    sales_officer_data = cache.get(cache_key)

    if sales_officer_data is None:
        # Fetch fresh from Google Sheets
        sales_officer_data = NewEmployeeData().consumer_so_data(unit_id)
        # Cache for 1 hour (3600 seconds)
        cache.set(cache_key, sales_officer_data, timeout=3600)

    # Exclude existing employees
    existing_emp = Employee.objects.values_list('EID', flat=True)
    filtered_data = {k: v for k, v in sales_officer_data.items() if k not in existing_emp}

    return JsonResponse({"results": filtered_data}, safe=False)

class SalesOfficerCreateView(CreateView, SuccessMessageMixin):
    model = Employee
    form_class = EmployeeEntryForm
    template_name = 'employees/sales_officer_CreateForm.html'
    success_url = '/employee/sales_officer/create'
    success_message = "Sales Officer Created Successfully"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        business_unit = BusinessUnit.objects.all()
        context['business_units'] = business_unit

        if self.request.POST:
            context['salary_formset'] = salesOfficerInfoFormset(self.request.POST)
            context['location_formset'] = salesOfficerLocationFormset(self.request.POST)
        else:
            context['salary_formset'] = salesOfficerInfoFormset()
            context['location_formset'] = salesOfficerLocationFormset()

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        salary_formset = context['salary_formset']
        location_formset = context['location_formset']

        if salary_formset.is_valid() and location_formset.is_valid():
            self.object = form.save()

            # attach the Employee to formsets
            salary_formset.instance = self.object
            location_formset.instance = self.object

            salary_formset.save()
            location_formset.save()

            unit_id = self.object.unit.id
            employee_id = self.object.EID
            joining_date = self.object.DOJ.strftime('%Y-%m-%d')
            update_sales_officer_joining_date_task.delay(unit_id, employee_id, joining_date)
            print("update successful")
            return redirect(self.success_url)

        return self.render_to_response(self.get_context_data(form=form))
