from .utils.google_form_Employees import NewEmployeeData
from celery import shared_task


@shared_task
def update_sales_officer_joining_date_task(unit_id, employee_id, joining_date):
    updater = NewEmployeeData()
    return updater.update_joining_date(unit_id, employee_id, joining_date)
