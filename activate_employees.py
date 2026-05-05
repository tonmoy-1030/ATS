import os
import django
import pandas as pd
from datetime import datetime

# === Setup Django environment ===
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ats.settings")
django.setup()

from employees.models import Employee, SeperationStatus

def activate_employees_from_excel(excel_file):
    if not os.path.exists(excel_file):
        print(f"File not found: {excel_file}")
        return

    try:
        df = pd.read_excel(excel_file)
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return

    # Normalize column names to handle spaces, newlines, etc.
    df.columns = df.columns.str.replace(r'\s+', ' ', regex=True).str.strip()
    
    # Try to find the ID column
    id_col = None
    possible_cols = ["Employee ID", "EID", "ID"]
    for col in df.columns:
        if col in possible_cols:
            id_col = col
            break
    
    if not id_col:
        print(f"Error: Could not find an ID column. Found: {df.columns.tolist()}")
        return

    activated, skipped = 0, 0

    for _, row in df.iterrows():
        eid = str(row.get(id_col, "")).strip()
        if not eid:
            skipped += 1
            continue

        try:
            employee = Employee.objects.get(EID=eid)
            # Try to find and delete separation status
            separation = SeperationStatus.objects.filter(employee=employee).first()
            if separation:
                separation.delete() # This will automatically set employee.active_status = True
                print(f"Reactivated employee {employee.name} (EID: {eid})")
                activated += 1
            else:
                # If no separation status, just ensure they are active
                if not employee.active_status:
                    employee.active_status = True
                    employee.save(update_fields=['active_status'])
                    print(f"Set active_status=True for {employee.name} (EID: {eid})")
                    activated += 1
                else:
                    print(f"Employee {employee.name} (EID: {eid}) is already active.")
                    skipped += 1
        except Employee.DoesNotExist:
            print(f"Employee with EID {eid} not found.")
            skipped += 1
        except Exception as e:
            print(f"Error processing EID {eid}: {e}")
            skipped += 1

    print(f"\nSummary:")
    print(f"Reactivated/Verified {activated} employees.")
    print(f"Skipped {skipped} entries.")


if __name__ == "__main__":
    file_path = r"C:\Users\tonmoy.hossain\Desktop\Resign.xlsx"
    activate_employees_from_excel(file_path)
