from django.shortcuts import render
from .forms import scheduleForm
from datetime import timedelta
import os
from django.shortcuts import render
from django.http import HttpResponse
from pyreportjasper import PyReportJasper
from .forms import scheduleForm, DailyJoiningForm
from datetime import timedelta
import tempfile  # To create temporary files
from django.http import HttpResponse
from pyreportjasper import PyReportJasper
from datetime import timedelta
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

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    
class DailyJoiningUpdateView(UpdateView):
    model = DailyJoining
    form_class = DailyJoiningForm
    template_name = 'report/daily_joining_form.html'
    success_url = '/report/daily_joining/'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    
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
    

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def get_daily_joinings(request):
    # Query the data from the DailyJoining model and order by date descending
    daily_joinings = DailyJoining.objects.all().values(
        'date', 
        'unit__short_name', 
        'location', 
        'recruitment_type', 
        'joinings_count'
    ).order_by('-date')  # Order by date in descending order

    # Convert the queryset to a pandas DataFrame
    df = pd.DataFrame(daily_joinings)

    # Ensure the 'date' column is in datetime format
    df['date'] = pd.to_datetime(df['date'])

    # Create the pivot table with a multi-level index (date, unit, recruitment_type)
    pivot_table = pd.pivot_table(
        df, 
        values='joinings_count', 
        index=['date'], 
        columns='unit__short_name', 
        aggfunc='sum', 
        margins=True, 
        margins_name='Totals', 
        fill_value=0
    )

    # Reset the index to flatten the pivot table (for easier rendering in the template)
    pivot_table = pivot_table.reset_index()

    # Convert the pivot table back to a list of dictionaries for rendering in the template
    table_data = pivot_table.to_dict('records')

    # Optionally format the date for template rendering
    for row in table_data:
        if row['date'] != 'Totals':
            row['date'] = pd.to_datetime(row['date']).strftime('%b %d, %Y')  # Format as Jan 04, 2025
    
    totals_row = None
    if 'Totals' in [row['date'] for row in table_data]:
        totals_row = next(row for row in table_data if row['date'] == 'Totals')
        table_data = [row for row in table_data if row['date'] != 'Totals']  # Remove 'Totals' row

    # Reverse the remaining data
    table_data.reverse()

    # Add the 'Totals' row back at the end
    if totals_row:
        table_data.append(totals_row)

    # Add pagination logic here
    paginator = Paginator(table_data, 10)  # Show 10 rows per page
    page = request.GET.get('page')  # Get the current page number from the request
    try:
        paginated_table_data = paginator.page(page)
    except PageNotAnInteger:
        paginated_table_data = paginator.page(1)  # If page is not an integer, show the first page
    except EmptyPage:
        paginated_table_data = paginator.page(paginator.num_pages)  # If page is out of range, show the last page

    # Prepare chart data (optional)
    chart_data = {
        'dates': [row['date'] for row in table_data if row['date'] != 'Totals'],
        'joinings': {
            unit: [row.get(unit, 0) for row in table_data if row['date'] != 'Totals']
            for unit in pivot_table.columns if unit != 'Totals'
        }
    }

    # Render the result in the template
    return render(request, 'report/daily_joining_report.html', {
        'table_data': paginated_table_data,  # Paginated table data
        'chart_data': chart_data
    })


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



