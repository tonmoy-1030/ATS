from django.db.models import F, ExpressionWrapper, DurationField, Avg
from django.db.models.functions import Coalesce
from django.utils import timezone
from jobs.models import Job
from django.views.generic import ListView
from candidates.models import Candidate, Offer
from django.db import connection
from explorer.models import Query
from decimal import Decimal
from plotly import graph_objects as go
from django.views import View
from django.http import JsonResponse
import pandas as pd
from .utils.jsonExporter import JSONExporter
import json
import plotly.express as px
from datetime import datetime


class DashBoard(ListView):
    template_name = 'dashboard/dashboard.html'
    model = Job

    def get_context_data(self, **kwargs):

        # Time to fill

        context = super().get_context_data(**kwargs)
        jobs = Job.objects.annotate(
            closing_time=Coalesce(F('closing_date'), timezone.now().date())
        ).annotate(
            time_to_fill=ExpressionWrapper(
                F('closing_time') - F('posting_date'),
                output_field=DurationField()
            )
        )
        ttf_by_unit = jobs.values('unit__short_name').annotate(avg_ttf=Avg('time_to_fill'))
        unit_labels = []
        avg_ttf_values = []
        for entry in ttf_by_unit:
            unit_labels.append(entry['unit__short_name'])
            avg_ttf_seconds = entry['avg_ttf'].total_seconds() if entry['avg_ttf'] else 0
            avg_ttf_values.append(avg_ttf_seconds / (60 * 60 * 24))

        # end

        # recruitment funnel

        shortlisted_candidate = Candidate.objects.all().count()
        initial_interview_stage = Candidate.objects.filter(attendance_status__icontains="present").count()
        final_interview_stage = Candidate.objects.filter(
            initial_interview_status__icontains="Forwarding for the next Interivew").count()
        offer = Offer.objects.all().count()
        hired = Offer.objects.filter(offer_status__icontains="Accepted").count()

        stage = ['Shortlisted Candidate', 'Initial Interview', 'Final Interview', 'Offer', 'Hired']
        count = [shortlisted_candidate, initial_interview_stage, final_interview_stage, offer, hired]

        fig = go.Figure(go.Funnel(y=stage, x=count,
                                  textposition="inside",
                                  textinfo="value+percent initial",
                                  opacity=1,
                                  marker={"color": ['#FF3784', '#36A2EB', '#4BC0C0', '#F77825', '#9966FF', '#00A8C6',
                                                    '#379F7A', '#CC2738', '#8B628A', '#8FBE00', '#606060'],
                                          "line": {"width": 0}
                                          }),
                        )

        fig.update_layout(
            title="Recruitment Funnel",
            title_font_size=20,
            title_x=0.5,
            funnelmode="stack",
            margin=dict(l=50, r=50, t=50, b=50),
            paper_bgcolor="rgba(0,0,0,0)",  # Dark background color for the chart paper
            plot_bgcolor="rgba(0,0,0,0)",   # Dark background color for the plot area
            font=dict(
                family="Times New Roman, serif",
                size=12,
                color='white'
            ),
            
            yaxis=dict(
                showticklabels=True  # Hide y-axis labels
            ),
            height=340
            
        )

        chart = fig.to_html()

        context['chart_funnel'] = chart

        # end

        raw_attrition_data = self.get_attrition_data()
        processed_data, months = process_attrition_data(raw_attrition_data)


        # first year attrition rate

        results = first_year_attrition()

        first_attrition_rates = [
            {
                "unit": row[0],
                "join_year": row[1],
                "total_joined": row[2],
                "total_left_within_first_year": row[3],
                "attrition_rate_percentage": float(row[4])  # Convert Decimal to float
            }
            for row in results
        ]

        data_2023 = [item for item in first_attrition_rates if item['join_year'] == 2023]
        data_2024 = [item for item in first_attrition_rates if item['join_year'] == 2024]

        # end

        # offer acceptance rate
        offer_acceptance_results = offer_acceptance_rate()

        offer_acceptance_rates = [{
            "acceptance_unit": row[0],
            "offer_acceptance": float(row[3])
        }
            for row in offer_acceptance_results
        ]
        service_lengths = ['More than 1 year', '9-12 months', '6-9 months', '3-6 months', 'Less than 3 months']
        
        interview_Frequency = interviewFrequency()
        candidatesTopUniversity = candidateTopEduInstitution()
        
        context['chart_interview'] = interview_Frequency
        context['chart_institution'] = candidatesTopUniversity
        context['chart_district'] = locationWiseCandidateHiring()
        # context['attrition_table'] = attritionTable()
        
    

        # Check for errors

        # end
  
        context['service_length'] = service_lengths
        context['offer_acceptance_rates'] = offer_acceptance_rates
        context['data_2023'] = data_2023
        context['data_2024'] = data_2024
        context['attrition_data'] = processed_data
        context['months'] = months
        context['unit_labels'] = unit_labels
        context['avg_ttf_values'] = avg_ttf_values
        context['stage'] = stage
        context['count'] = count

        return context

    def get_attrition_data(self):
        query_id = 3
        query = Query.objects.get(id=query_id)

        with connection.cursor() as cursor:
            cursor.execute(query.sql)
            columns = [col[0] for col in cursor.description]
            results = []
            for row in cursor.fetchall():
                row_dict = dict(zip(columns, row))
                results.append(row_dict)
        return results


def process_attrition_data(raw_data):
    # Initialize a dictionary to hold the processed data
    processed_data = {}
    months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

    for entry in raw_data:
        unit = entry['unit']
        month = entry['month']
        attrition_rate = entry['attrition_rate']

        if unit not in processed_data:
            # Initialize the dictionary for the unit with all months set to zero attrition rate
            processed_data[unit] = {m: Decimal('0.0') for m in months}

        # Update the attrition rate for the corresponding month
        processed_data[unit][month] = attrition_rate

    return processed_data, months

from .utils.jsonExporter import JSONExporter

def first_year_attrition():
    query_id = 7
    query = Query.objects.get(id=query_id)
    exporter = JSONExporter(query)
    data = exporter.get_output()
    with connection.cursor() as cursor:
        cursor.execute(query.sql)
        results = cursor.fetchall()

        return results


def offer_acceptance_rate():
    query_id = 8
    query = Query.objects.get(id=query_id)
    with connection.cursor() as cursor:
        cursor.execute(query.sql)
        results = cursor.fetchall()
        return results


class SeparatedEMPJsonView(View):
    def get(self, request):
        selected_value = request.GET.get("where", "")

        if selected_value != "MGT":
            where = ""
        else:
            where = '''
            WHERE e.eid NOT LIKE 'PC%'
            AND e.EID NOT LIKE 'TKF%'
            AND e.designation != 'Helper'
            '''

        query= f'''
        SELECT jobs_businessunit.short_name AS Unit,
        COUNT(e.id) AS 'No. of Employees',
        CASE
            WHEN DATEDIFF(employees_seperationstatus.resign_date, e.DOJ) / 365.0 < 0.25 THEN 'Less than 3 months'
            WHEN DATEDIFF(employees_seperationstatus.resign_date, e.DOJ) / 365.0 >= 0.25
                    AND DATEDIFF(employees_seperationstatus.resign_date, e.DOJ) / 365.0 < 0.5 THEN '3-6 months'
            WHEN DATEDIFF(employees_seperationstatus.resign_date, e.DOJ) / 365.0 >= 0.5
                    AND DATEDIFF(employees_seperationstatus.resign_date, e.DOJ) / 365.0 < 0.75 THEN '6-9 months'
            WHEN DATEDIFF(employees_seperationstatus.resign_date, e.DOJ) / 365.0 >= 0.75
                    AND DATEDIFF(employees_seperationstatus.resign_date, e.DOJ) / 365.0 < 1 THEN '9-12 months'
            ELSE 'More than 1 year'
        END AS Duration_Category
            FROM employees_employee e
            JOIN employees_seperationstatus ON e.id = employees_seperationstatus.employee_id
            JOIN jobs_businessunit ON e.unit_id = jobs_businessunit.id
            {where}
            GROUP BY jobs_businessunit.short_name,
                    Duration_Category
            ORDER BY jobs_businessunit.short_name,
                    Duration_Category;
                '''
        with connection.cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                # Execute your query based on the selected value
                processed_data = {}
                service_lengths = ['More than 1 year', '9-12 months', '6-9 months', '3-6 months', 'Less than 3 months']

                for entry in results:
                    unit = entry[0]
                    No_of_Employees = entry[1]
                    service_length = entry[2]
                    
                    if unit not in processed_data:
                        # Initialize the dictionary for the unit with all months set to zero attrition rate
                        processed_data[unit] = {m: Decimal(0) for m in service_lengths}
                    # Update the attrition rate for the corresponding month
                    processed_data[unit][service_length] = Decimal(No_of_Employees)

        return JsonResponse({'data': processed_data})

def interviewFrequency():
    query = Query.objects.get(id=16)
    exporter = JSONExporter(query)
    data = exporter.get_output()
    
    data_list = json.loads(data)
    df = pd.DataFrame(data_list)
    
    # Create a figure
    fig = go.Figure()

    # Add separate traces for each interview type
    for interview_type in df['interview_type'].unique():
        trace_data = df[df['interview_type'] == interview_type]
        fig.add_trace(go.Scatter(
            x=trace_data['MONTH'],
            y=trace_data['Frequency'],
            mode='lines+markers+text',
            name=interview_type,
            text=trace_data['Frequency'],
            textposition='top center',
            hovertemplate='<b>Month:</b> %{x}<br><b>Frequency:</b> %{y}<br><b>Type:</b> ' + interview_type,
            line=dict(width=2),
            marker=dict(size=8, symbol="circle")
        ))

    # Update layout for better aesthetics
    fig.update_layout(
        title={'text': 'Monthly Interview Frequency', 'x': 0.5, 'xanchor': 'center'},
        xaxis_title="Month",
        yaxis_title="Number of Interviews",
        legend_title="Interview Type",
        font=dict(
            family="Arial, sans-serif",
            size=14,
            color="white"
        ),
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        xaxis=dict(
            showgrid=False,
            tickmode='linear'  # Ensure all months are shown
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.2)'
        )
    )
    
    interview_line = fig.to_html(full_html=False)
    
    return interview_line

def candidateTopEduInstitution():
    query_id = 17
    query = Query.objects.get(id=query_id)
    exporter = JSONExporter(query)
    data = exporter.get_output()
    # data_list = json.loads
    df = pd.DataFrame(json.loads(data))
    fig = px.bar(df,x='institution_highest_degree', y='NO', text='NO', template="plotly_dark", color= 'institution_highest_degree')
    fig.update_layout(
        title={'text': 'Top 5 University', 'x': 0.5, 'xanchor': 'center'},
        xaxis_title="University",
        yaxis_title="Frequency",
        font=dict(
            family="Times New Roman, serif",
            size=14,
            color='white'
        ),
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        xaxis=dict(
            showgrid=False,
            tickmode='linear'  # Ensure all months are shown
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.2)'
        )
    )
    fig = fig.to_html(full_html=False)
    return fig

def locationWiseCandidateHiring():
    query_id = 18
    query = Query.objects.get(id=query_id)
    exporter = JSONExporter(query)
    data = exporter.get_output()
    # data_list = json.loads
    df = pd.DataFrame(json.loads(data))
    fig = px.bar(df,x='Permanent District', y='NO', text='NO', template="plotly_dark", color= 'Permanent District')
    
    fig.update_layout(
        title={'text': 'Top 10 District', 'x': 0.5, 'xanchor': 'center'},
        xaxis_title="District",
        yaxis_title="No of District",
        font=dict(
            family="Times New Roman, serif",
            size=14,
            color='white'
        ),
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        xaxis=dict(
            showgrid=False,
            tickmode='linear'  # Ensure all months are shown
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.2)'
        )
    )

    
    fig = fig.to_html(full_html=False)
    return fig
