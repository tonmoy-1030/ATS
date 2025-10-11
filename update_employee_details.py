import os
import django
import pandas as pd
from datetime import datetime

# === Setup Django environment ===
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ats.settings")  # change 'ats' to your project name
django.setup()

from employees.models import Employee, EmployeeDetails


def parse_date(value):
    """Convert Excel date/string to Python date in YYYY-MM-DD format or None."""
    if pd.isna(value) or value == "":
        return None
    if isinstance(value, datetime):
        return value.date()
    try:
        # Try parsing from string with flexible formats
        return pd.to_datetime(value, errors="coerce").date()
    except Exception:
        return None


def update_employee_details_from_excel(excel_file):
    df = pd.read_excel(excel_file)
    df.columns = df.columns.str.strip()

    updated, skipped = 0, 0

    for _, row in df.iterrows():
        eid = str(row.get("EID", "")).strip()
        if not eid:
            skipped += 1
            continue

        try:
            employee = Employee.objects.get(EID=eid)
        except Employee.DoesNotExist:
            print(f"❌ Employee with EID {eid} not found.")
            skipped += 1
            continue
        
        details, created = EmployeeDetails.objects.get_or_create(employee=employee)
        employee.mobile_no=row.get("Personal Mobile No.", "")
        employee.email=row.get("Email", "").strip()
        
        employee.save()
        # Personal Info
        details.date_of_birth = parse_date(row.get("Date of Birth"))
        details.blood_group = row.get("Blood Group", "")
        details.father_name = row.get("Father's Name", "")
        details.mother_name = row.get("Mother's Name", "")
        details.marital_status = row.get("Marital Status", "")
        details.spouse_name = row.get("Spouse Name", "")
        details.no_of_son = row.get("Number of Son")
        details.no_of_daughter = row.get("Number of Daughter")

        # Contact Info
        details.official_mobile = row.get("Official Mobile No.", "")
        details.emergency_contact_person = row.get("Emergency Contact Person Name", "")
        details.emergency_contact_no = row.get("Emergency Contact Mobile No.", "")
        details.emer_relation_with_employee = row.get("Relationship with Employee", "")

        details.present_vill = row.get("Present Vill", "")
        details.present_po = row.get("P.O", "")
        details.present_ps = row.get("P.S", "")
        details.present_dist = row.get("Present District", "")

        details.permanent_vill = row.get("Permanent Vill", "")
        details.permanent_po = row.get("P.O.1", "")
        details.permanent_ps = row.get("P.S.1", "")
        details.permanent_dist = row.get("Permanent District", "")

        # Education
        details.highest_degree = row.get("Degree Name", "")
        details.subject_highest_degree = row.get("Subject/Group", "")
        details.institution_highest_degree = row.get("Institution", "")
        details.passing_year_highest_degree = row.get("Passing Year", "")
        details.division_or_gpa_highest_degree = row.get("Division/CGPA/GPA", "")

        details.professional_degree = row.get("Professional Degree", "")
        details.subject_professional_degree = row.get("Subject", "")
        details.institution_professional_degree = row.get("Institution.1", "")
        details.passing_year_professional_degree = row.get("Passing Year.1", "")

        # IDs
        details.nid = row.get("NID/Birth Certificate No.", "")
        details.tin = row.get("TIN No. (If any)", "")
        details.religion = row.get("Religion", "")

        details.save()
        updated += 1

    print(f"✅ Updated {updated} employees, skipped {skipped}.")


if __name__ == "__main__":
    update_employee_details_from_excel("C:\\Users\\tonmoy.hossain\\Desktop\\Old Employee Information Form (Responses).xlsx")
