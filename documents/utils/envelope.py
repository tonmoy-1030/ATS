from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4, letter

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer, Frame
from reportlab.lib import colors
import os
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from datetime import datetime


def create_envelope(file_path, employee_info):

    width, height = 9.5 * inch, 4.13 * inch

    c = canvas.Canvas(file_path, pagesize=(width, height))

    recipient_address = [
        
        f"{employee_info['name']}",
        f"{employee_info['designation']}",
        f"ID: {employee_info['EID']}",
    ]
    c.setFont("Times-Bold", 11)
    y = height - 1.5 * inch  
    for line in recipient_address:
        c.drawString(5 * inch, y, line)  
        y -= 0.25 * inch  

    c.save()

def createNameTag(file_path, employee_info):
   
    # Create a list to hold the flowable objects
    flowables = []

    # Define styles
    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    normal_style = styles["Normal"]
    normal_style.leading = 15
    styles["Normal"].fontName = "Times-Roman"
    normal_style.fontSize  = 12
    title_style.fontName = "Times-Roman"
    title_style.fontSize = 14

    # Offer letter content
    offer_letter_content = [
        "<br/>"
    
    ]

    for line in offer_letter_content:
        flowables.append(Paragraph(line, normal_style))

        
    doc = SimpleDocTemplate(file_path, pagesize=landscape(letter))
    doc.build(flowables, onFirstPage=lambda canvas, doc: onfirstpage(canvas, doc, employee_info))

  
def onfirstpage(canvas, doc, employee_info):
    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    normal_style = styles["Normal"]
    normal_style.leading = 15
    styles["Normal"].fontName = "Times-Roman"
    normal_style.fontSize  = 12
    title_style.fontName = "Times-bold"
    title_style.fontSize = 20
    title_style.alignment = 1
    title_style.leading = 25

    flowables = []
    #add some flowables
    flowables.append(Paragraph(
                                f"""<br/>
                                <b>{employee_info['name']}<br/>
                                    {employee_info['designation']}<br/>
                                    D.O.J:  {employee_info['doj'].strftime("%d-%b-%y")}
                                    </b>
                                    <br/>
                                """,
                               title_style
                               )
                     )
    flowables.append(Spacer(1, 0.1 * inch))
    f = Frame(2*inch, 6*inch, 7.44*inch, 1.96*inch, showBoundary=1)
    f.addFromList(flowables, canvas)
    
    flowables.append(Paragraph(
                                f"""
                                <b>{employee_info['EID']}</b>
                                """,
                               title_style
                               )
                     )
    id_1 = Frame(2*inch, 5*inch, 2*inch, .6*inch, bottomPadding=0, showBoundary=1)
    
    id_1.addFromList(flowables, canvas)
    flowables.append(Paragraph(
                                f"""
                                
                                <b>{employee_info['EID']}</b>
                                    
                                """,
                               title_style
                               ))
    id_2 = Frame(2*inch, 4.2*inch, 2*inch, .6*inch, bottomPadding=0, showBoundary=1)
    id_2.addFromList(flowables, canvas)    

