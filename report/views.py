from django.shortcuts import render, redirect
from django.urls import reverse
from datetime import timedelta
import os
from django.http import HttpResponse
from .forms import scheduleForm, DailyJoiningForm
import tempfile  # To create temporary files
from pyreportjasper import PyReportJasper
from employees.forms import EmployeeFilter
from employees.models import Employee
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import DailyJoining
from django.views.generic.list import ListView
import pandas as pd





os.environ['JAVA_HOME'] = r"C:\Program Files\Java\jdk-17"
os.environ['PATH'] = os.environ['PATH'] + os.pathsep + os.path.join(os.environ['JAVA_HOME'], 'bin')

# Create your views here.


# candidates_token = os.path.join(project_root, 'utls/candidates_token.json')
# credentials_files = os.path.join(project_root, 'utls/credentials.json')

# Define the resources directory
RESOURCES_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'resources')

# Daily Joining
class DailyJoiningCreateView(CreateView):
    model = DailyJoining
    form_class = DailyJoiningForm
    template_name = 'report/daily_joining_form.html'
    success_url = '/report/daily_joining/'

    def get_form_kwargs(self):
        # Get the default form kwargs and add the user
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Assign the logged-in user to the form instance (if applicable)
        form.instance.user = self.request.user
        return super().form_valid(form)

    
class DailyJoiningUpdateView(UpdateView):
    model = DailyJoining
    form_class = DailyJoiningForm
    template_name = 'report/daily_joining_form.html'
    success_url = '/report/daily_joining/'

    def get_form_kwargs(self):
        # Get the default form kwargs and add the user
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Assign the logged-in user to the form instance (if applicable)
        form.instance.user = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('report:daily_joining_list')
    
class DailyJoiningDeleteView(DeleteView):
    model = DailyJoining
    template_name = 'report/daily_joining_delete.html'
    success_url = '/report/daily_joining/list'
    
class DailyJoiningListView(ListView):
    model = DailyJoining
    template_name = 'report/daily_joining_list.html'
    context_object_name = 'joinings'
    paginate_by = 10
    ordering = ['-date', 'unit']
    
    def get_queryset(self):
        return DailyJoining.objects.filter(user=self.request.user).order_by('-date', 'unit')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Daily Joining List'
        return context

class DailyJoiningReportView(ListView):
    model = DailyJoining
    template_name = 'report/daily_joining_report.html'
    context_object_name = 'joinings'
    paginate_by = 10
    ordering = ['-date', 'unit']
    
    def get_queryset(self):
        print(DailyJoining.objects.all().order_by('-date', 'unit'))
        return DailyJoining.objects.all().order_by('-date', 'unit')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Daily Joining Report'
        return context
    

def get_daily_joinings(request):
    # Query the data from the DailyJoining model and order by date descending
    daily_joinings = DailyJoining.objects.all().values(
        'date',
        'unit__short_name',
        'location',
        'employee_category',
        'recruitment_type',
        'joinings_count'
    ).order_by('-date')  # Order by date in descending order

    # Convert the queryset to a pandas DataFrame
    df = pd.DataFrame(daily_joinings)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['date'] = df['date'].dt.strftime('%d-%b-%y')

    # Create the pivot table with a multi-level index (date, unit, location, category)
    pivot_table = pd.pivot_table(
        df,
        values='joinings_count',
        index=['unit__short_name', 'location', 'employee_category'],
        columns=['date'],
        aggfunc='sum',
        margins=True,
        margins_name='Total',
        fill_value=""
    )

    # Reset the index to flatten the pivot table (for easier rendering in the template)
    pivot_table = pivot_table.reset_index()
    # pivot_table['date'] = pivot_table['date'].apply(lambda x: x.strftime('%d-%b-%y') if not pd.isnull(x) else x)
    
    # Prepare the data for template rendering
    table_data = pivot_table.to_dict('records')
    # Extract the dynamic headers in hierarchical format (unit -> location -> category)
    
    timestamp_keys  = list(table_data[0].keys())[3:-1]
    
    unit_counts = {}
    for row in table_data:
        unit = row['unit__short_name']
        unit_counts[unit] = unit_counts.get(unit, 0) + 1
        
    # Render the result in the template
    return render(request, 'report/daily_joining_report.html', {'rows': table_data, 'timestamp_keys': timestamp_keys, 'unit_counts': unit_counts}
    )


def interviewSchedule(request):
    settings_dir = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.dirname(settings_dir))
    input_file = os.path.join(project_root, 'report/resources/Interview_schedule.jrxml')

    if request.method == "POST":
        form = scheduleForm(request.POST)
        if form.is_valid():
            from_date = form.cleaned_data.get("from_date")
            to_date = form.cleaned_data.get("to_date")
            unit = form.cleaned_data.get('unit')
            format_ = form.cleaned_data.get("format_")  # The selected format (e.g., 'pdf', 'docx', 'xls')

            # Handle single or multiple units
            if len(unit) > 1:
                unit = tuple(unit)
            else:
                unit = unit[0]  # Take the single unit directly

            # Ensure from_date and to_date are provided
            if not from_date or not to_date:
                return render(request, "report/interviewSchedule.html", {
                    'form': form,
                    'error': 'Please provide both from and to dates.'
                })

            # Format the dates for the report
            from_date_str = from_date.strftime('%Y-%m-%d')
            to_date_str = (to_date + timedelta(days=1)).strftime('%Y-%m-%d')

            # Create PyReportJasper object
            jasper = PyReportJasper()

            # Define parameters for the report
            param = {
                'startDate': from_date_str,
                'endDate': to_date_str,
                'businessUnit': unit
            }

            # Create a temporary file to hold the output
            with tempfile.NamedTemporaryFile(suffix=f'.{format_}', delete=False) as temp_file:
                output_file_path = temp_file.name  # Get the temporary file path

            # Configure the report with MySQL database connection
            jasper.config(
                input_file=input_file,
                output_file=output_file_path,  # Save output to the temporary file
                parameters=param,
                output_formats=[format_],  # Output in the selected format
                db_connection={
                    'driver': 'mysql',
                    'username': 'root',
                    'password': 'Tonmoy1030',
                    'host': 'localhost',
                    'database': 'atsdb',
                    'port': '3306',
                    'jdbc_driver': 'com.mysql.cj.jdbc.Driver',
                    'jdbc_url': 'jdbc:mysql://localhost:3306/atsdb'
                }
            )

            # Process the report and generate the output in the temporary file
            jasper.process_report()

            # Read the generated file from the temporary file
            with open(output_file_path, 'rb') as output_file:
                response = HttpResponse(output_file.read(), content_type='application/octet-stream')
                response['Content-Disposition'] = f'attachment; filename="Interview_Schedule.{format_}"'
                return response
    else:
        form = scheduleForm()

    return render(request, "report/interviewSchedule.html", context={'form': form})

def employee_list_bond(request):
    # filtering the employee list only which has details
    employee_filter = EmployeeFilter(request.GET, queryset=Employee.objects.filter(details__isnull=False, unit_id=1).order_by('-DOJ'))
    
    paginator = Paginator(employee_filter.qs, 10)  
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    return render(request, 'report/employee_Bond_form.html', {'filter': employee_filter, 'page_obj': page_obj})



def BondPaper(request):
    settings_dir = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.dirname(settings_dir))
    input_file = os.path.join(project_root, 'report/resources/Bond.jrxml')

    if request.method == "POST":
        # Get the selected employee
        employee_list = request.POST.get('employees_list')
        if not employee_list:
            return HttpResponse("No employee selected.", status=400)
        employee = Employee.objects.get(EID=employee_list)
        

        # Create PyReportJasper object
        jasper = PyReportJasper()

        # Define parameters for the report
        param = {
            'EMP_ID': employee.EID
        }

        # Create a temporary file to hold the output
        with tempfile.NamedTemporaryFile(suffix=f'.pdf', delete=False) as temp_file:
            output_file_path = temp_file.name  # Get the temporary file path

        # Configure the report with MySQL database connection
        jasper.config(
            input_file=input_file,
            output_file=output_file_path,  # Save output to the temporary file
            parameters=param,
            output_formats=['pdf'],  # Output in the selected format
            db_connection={
                'driver': 'mysql',
                'username': 'root',
                'password': 'Tonmoy1030',
                'host': 'localhost',
                'database': 'atsdb',
                'port': '3306',
                'jdbc_driver': 'com.mysql.cj.jdbc.Driver',
                'jdbc_url': 'jdbc:mysql://localhost:3306/atsdb'
            }
        )

        # Process the report and generate the output in the temporary file
        jasper.process_report()

        # Read the generated file from the temporary file
        with open(output_file_path, 'rb') as output_file:
            response = HttpResponse(output_file.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="{employee.EID}_{employee.name}_Bond.pdf"'
            return response



