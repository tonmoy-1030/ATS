from django.shortcuts import render
from .forms import scheduleForm
from datetime import timedelta
import os

os.environ['JAVA_HOME'] = r"C:\Program Files\Java\jdk-17"
os.environ['PATH'] = os.environ['PATH'] + os.pathsep + os.path.join(os.environ['JAVA_HOME'], 'bin')

# Create your views here.
import os
import io  # To handle in-memory file (buffer)
from django.shortcuts import render
from django.http import HttpResponse
from pyreportjasper import PyReportJasper
from .forms import scheduleForm
from datetime import timedelta


# candidates_token = os.path.join(project_root, 'utls/candidates_token.json')
# credentials_files = os.path.join(project_root, 'utls/credentials.json')

# Define the resources directory
RESOURCES_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'resources')

import os
import io  # To handle in-memory file (buffer)
import tempfile  # To create temporary files
from django.shortcuts import render
from django.http import HttpResponse
from pyreportjasper import PyReportJasper
from .forms import scheduleForm
from datetime import timedelta

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
