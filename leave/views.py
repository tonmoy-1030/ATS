from django.shortcuts import render, redirect
from .models import LeaveApplication, LeaveAllocation, Holiday
from .forms import LeaveAllocationForm, LeaveApplicationForm, LeaveFilter, LeaveAllocationFilter, HolidayForm, HolidayFilter
from django.views.generic import CreateView, UpdateView, DeleteView
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django.views.decorators.http import require_GET
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from django.db import IntegrityError
import os
import csv


class LeaveAllocationCreateView(CreateView, SuccessMessageMixin):
    model = LeaveAllocation
    form_class = LeaveAllocationForm
    template_name = "leaves/leaveAllocation.html"
    success_url = "/leaves/allocation"
    success_message = "Leave allocated Successfully"
    
class LeaveAllocationUpdateView(UpdateView, SuccessMessageMixin):
    model = LeaveAllocation
    form_class = LeaveAllocationForm
    template_name = "leaves/leaveAllocation.html"
    success_url = "/leaves/allocation/list"
    success_message = "Leave allocated Successfully"

class LeaveAllocationDeleteView(DeleteView):
    model = LeaveAllocation
    success_url = "/leaves/allocation/list"

# Leave Application Entry     
class LeaveApplicationCreateView(CreateView, SuccessMessageMixin):
    model = LeaveApplication
    form_class = LeaveApplicationForm
    template_name = "leaves/leaveApplication.html"
    success_url = "/leaves/application"
    success_message = "Leave application Entered Successfully"

# Leave Application Update
class LeaveApplicationUpdateView(UpdateView, SuccessMessageMixin):
    model = LeaveApplication
    form_class = LeaveApplicationForm
    template_name = "leaves/leaveApplication.html"
    success_url = "/leaves/application/list"
    success_message = "Leave application updated Successfully"


class LeaveApplicationDeleteView(DeleteView):
    model = LeaveApplication
    success_url = "/leaves/application/list"
    
    
class HolidayCreateView(CreateView):
    model = Holiday
    form_class = HolidayForm
    template_name = "leaves/holiday.html"
    success_url = "/leaves/holiday"
    

class HolidayUpdateView(UpdateView):
    model = Holiday
    form_class = HolidayForm
    template_name = "leaves/holiday.html"
    success_url = "/leaves/holiday/list"

# Leave Application List
def LeaveApplicationList(request):
    leave_filter = LeaveFilter(request.GET, queryset=LeaveApplication.objects.all())
    paginator = Paginator(leave_filter.qs, 12)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    return render(request, 'leaves/leaveApplicationList.html', {'filter': leave_filter, 'page_obj': page_obj})
  
  
# Leave Allocation List
def LeaveAllocationList(request):
    allocation_filter = LeaveAllocationFilter(request.GET, queryset=LeaveAllocation.objects.all().order_by('year', 'employee__EID'))
    paginator = Paginator(allocation_filter.qs, 12)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    return render(request, 'leaves/leaveAllocationList.html', {'filter': allocation_filter, 'page_obj': page_obj})


def holidayList(request):
    holiday_filter = HolidayFilter(request.GET, queryset=Holiday.objects.all().order_by('-date'))
    paginator = Paginator(holiday_filter.qs, 12)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    return render(request, 'leaves/holidayList.html', {'filter': holiday_filter, 'page_obj': page_obj})


# Function of Calculating Start Days and End Days
@require_GET
def calculate_leave_days(request):
    try:
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = timezone.datetime.strptime(end_date_str, '%Y-%m-%d').date()

        if start_date > end_date:
            return JsonResponse({'error': 'Start date cannot be after end date.'}, status=400)

        holidays = Holiday.objects.filter(date__range=[start_date, end_date]).values_list('date', flat=True)
        current_date = start_date
        total_days = 0

        while current_date <= end_date:
            if current_date.weekday() == 4:
                pass
            elif current_date.weekday() == 5:
                total_days += 0.5
            elif current_date.weekday() <= 7 and current_date not in holidays:
                total_days += 1
            current_date += timezone.timedelta(days=1)

        return JsonResponse({'total_days': total_days})

    except ValueError:
        return JsonResponse({'error': 'Invalid date format.'}, status=400)
    
from employees.models import Employee
from .models import LeaveType
from django.db import IntegrityError, transaction

def import_employees(file):
    # Create a temporary directory to store the uploaded file
    temp_directory = os.path.join(settings.MEDIA_ROOT, 'temp')
    os.makedirs(temp_directory, exist_ok=True)

    # Save the uploaded file to the temporary directory
    temp_file_path = os.path.join(temp_directory, file.name)
    with open(temp_file_path, 'wb') as temp_file:
        for chunk in file.chunks():
            temp_file.write(chunk)

    try:
        # Use a transaction to ensure all-or-nothing operation
        with transaction.atomic():
            # Open the CSV file for reading
            with open(temp_file_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        # Convert string values to the appropriate type
                        employee_id = int(row['id'].strip())  # Assuming the CSV has EID as employee_id
                        leave_type_name = row['leave_type'].strip()
                        year = int(row['year'].strip())
                        
                        # Handle conversion for numeric fields with error checking
                        leave_allocated = float(row['leave_allocated'].strip())
                        leave_taken = float(row['leave_taken'].strip()) if row['leave_taken'].strip() not in ('', '-', ' - ') else 0.0
                        leave_balance = float(row['leave_balance'].strip())

                        # Get the Employee and LeaveType objects
                        employee = Employee.objects.get(id=employee_id)
                        leave_type = LeaveType.objects.get(name=leave_type_name)

                        # Update or create the LeaveAllocation object
                        allocation, created = LeaveAllocation.objects.update_or_create(
                            employee=employee,
                            leave_type=leave_type,
                            year=year,
                            defaults={
                                'leave_allocated': leave_allocated,
                                'leave_taken': leave_taken,
                                'leave_balance': leave_balance,
                            }
                        )
                    except (ValueError, Employee.DoesNotExist, LeaveType.DoesNotExist) as e:
                        # Skip rows with invalid data or missing foreign key references
                        print(f"Skipping row {row} due to error: {str(e)}")
                        continue

    except IntegrityError:
        # Handle transaction integrity errors
        return HttpResponse("An error occurred while importing the data. Please check the CSV file and try again.")

    # Remove the temporary file after processing
    os.remove(temp_file_path)

    return HttpResponse("Employee data imported successfully.")

from .forms import UploadFileForm

def upload_file(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            import_employees(request.FILES["file"])
            return HttpResponseRedirect("/leaves/allocation/list")
    else:
        form = UploadFileForm()
    return render(request, "leaves/upload.html", {"form": form})