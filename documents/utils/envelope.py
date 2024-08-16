from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

def create_envelope(file_path, employee_info):

    width, height = 9.5 * inch, 4.13 * inch

    c = canvas.Canvas(file_path, pagesize=(width, height))

    recipient_address = [
        
        f"{employee_info['name']}",
        f"{employee_info['designation']}",
        f"ID: {employee_info['EID']}",
    ]
    c.setFont("Times-Bold", 12)
    y = height - 1.5 * inch  
    for line in recipient_address:
        c.drawString(5 * inch, y, line)  
        y -= 0.25 * inch  

    c.save()

