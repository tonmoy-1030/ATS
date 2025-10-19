from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer, Frame
from reportlab.lib import colors
import os
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch



def interview_assessment(candidate_data, pdf_path):
    settings_dir = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.dirname(settings_dir))
    logo_path = os.path.join(project_root, 'logo.png')
  
    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.setFont("Helvetica", 12)
    
    #Logo  
    c.drawImage(logo_path, 280, 730, width=48.62, height=58.32, mask='auto')
    #Set the reference
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(480, 720, "Form: IAS/01-2019 (Annexure-F)")
    #set title
    c.setFont("Helvetica-Bold", 14)
    line_width = 1.5
    text = "Interview Assessment Sheet"
    text_width = c.stringWidth(text)
    start_x = 216
    start_y = 700 - 2 * line_width
    end_x = start_x + text_width
    end_y = start_y
    c.line(start_x, start_y, end_x, end_y)
    start_y -= line_width * 1.5
    end_y -= line_width * 1.5
    c.line(start_x, start_y, end_x, end_y)
    c.drawString(216, 700, text)
    #name field
    c.setFont("Helvetica", 11)
    c.drawString(50, 670, f"Date: {candidate_data['date'].strftime('%d-%b-%y')}")
    c.drawString(50, 650, f"Name of Candidate: {candidate_data['name']}")
    c.drawString(50, 630, f"Applied for:  {candidate_data['applied_for']}")
    c.drawString(50, 610, f"Educational Qualification: {candidate_data['educational_qualification']}")
    c.drawString(350, 630, f"Unit: {candidate_data['unit']}")
    c.drawString(350, 610, f"Age: {candidate_data['age']}")
    c.drawString(50, 590, f"Experience: {candidate_data['total_experience']} Years")
    c.drawString(350, 590, "Present Position Held:")
    c.drawString(50, 570, "Present Drawn Salary: Tk ……………………")
    c.drawString(350, 570, "Other Benefits (if any): Tk …………………")
    c.drawString(50, 550, "Expected Salary: Tk ……………………")
    c.drawString(50, 530, "Negotiated Salary: Tk ……………………")
    c.drawString(350, 550, "Notice Period: ……………………")
    c.drawString(50, 510, "Reason to change previous job? …………………………………………………………………………………")
    
    #table
    data = [
      ['SL', 'Assessment Criteria', 'Marks Allotted', 'Marks Obtained', 'Remarks'],
      ['1','Related experience in similar role ', '25'],
      ['2', 'Job Knowledge', '20'],
      ['3', 'Academic Background', '20'],
      ['4', 'Communication Ability', '15'],
      ['5', 'Attitude / Confidence Leve ', '10'],
      ['6', 'Appearance & Presentation', '10'],
      ['Total']
    ]
    
    
    style = TableStyle([
      ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#D7E4BC")),
      ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
      ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
      ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
      ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
      ('BOX', (0,0), (-1,-1), 0.25, colors.black),
      ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
    ])
        
    col_widths = [30, 163, 80, 80, 200]
    table = Table(data, colWidths=col_widths)
    table.setStyle(style)

    
    table_style = TableStyle([
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('ALIGN', (1, 1), (1, 6), 'LEFT'),
        ('SPAN', (0, 7), (1, 7)),
        ('BACKGROUND', (0, 7), (1, 7), colors.HexColor("#D7E4BC")),
        ('ROWHEIGHT', (0, 0), (-1, -1),100)
    ])

    table.setStyle(table_style)
    
    # Draw table on canvas
    table.wrapOn(c,  0, 0)
    table.drawOn(c, 50, 280)   
    
    #Overall Rating

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50,260, "OVERALL RATING (Put √):")
    c.rect(50, 200, 100, 50)
    text_content = """
    OUTSTANDING
    91% & Above 
    """
    lines = text_content.split("\n")
    text_y = 200 + 40
    for line in lines:
        c.drawString(45, text_y, line)
        text_y -= 15
        
        
    c.rect(155, 200, 100, 50)
    text_content = """
    EXCELLENT
    81% to 90%
    """
    lines = text_content.split("\n")
    text_y = 200 + 50-10
    for line in lines:
        c.drawString(155, text_y, line)
        text_y -= 15
        
    c.rect(260, 200, 120, 50)
    text_content = """
    ABOVE AVERAGE
    65% to 80%
    """
    lines = text_content.split("\n")
    text_y = 200 + 50-10
    for line in lines:
        c.drawString(255, text_y, line)
        text_y -= 15 
        
        
    c.rect(385, 200, 90, 50)
    text_content = """
    AVERAGE
    50% to 64%
    """
    lines = text_content.split("\n")
    text_y = 200 + 50-10
    for line in lines:
        c.drawString(385, text_y, line)
        text_y -= 15 
        
    c.rect(480, 200, 125, 50)
    text_content = """
    BELOW AVERAGE
    Below 50%
    """
    lines = text_content.split("\n")
    text_y = 200 + 50-10
    for line in lines:
        c.drawString(475, text_y, line)
        text_y -= 15
                 
    #Recommendation
    c.drawString(50,180, "OVERALL REMARKS:")    
    c.drawString(50,165, "…………………………………………………………………………………………………………………………")  
    c.drawString(50,140, "…………………………………………………………………………………………………………………………")
    c.drawString(50,110, "RECOMMENDATION:")
    c.rect(175, 110, 10, 10)
    c.drawString(190,110, "Deferred")
    c.rect(420, 110, 10, 10)
    c.drawString(435,110, "Waiting List")
    c.rect(175, 80, 10, 10)
    c.drawString(190,80, "Forwarded for Next Interview")
    c.rect(420, 80, 10, 10)
    c.drawString(435,80, "Immediate Recruitment")
    
    #Interview By
    c.drawString(50,50, "INTERVIEWED BY:") 
    c.drawString(175,40, "…………………………")
    c.drawString(320,40, "…………………………")
    c.drawString(465,40, "…………………………")
    
    c.drawString(205,25, "Signature")
    c.drawString(350,25, "Signature")
    c.drawString(495,25, "Signature")
      
    #save the pdf
    c.save()
    

def create_offer_letter(pdf_file,candidate_data):
    from datetime import datetime
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
    title_style.fontsize = 14

    # Offer letter content
    offer_letter_content = [
        "<br/>"
        f"<br/>{candidate_data['ref']}",
        f"<b>{datetime.now().date().strftime('%d-%b-%Y')}</b>",
        f'<b>Mr. {candidate_data['name']}</b> <br/>Vill: {candidate_data['vill']} \
        P.O: {candidate_data['po']} <br/> P.S: {candidate_data['ps']} Dist: {candidate_data['dist']}'
    ]

    for line in offer_letter_content:
        flowables.append(Paragraph(line, normal_style))
    
    title = "Offer Letter"
    title_text = Paragraph("<b><u>{}</u></b>".format(title), title_style)
    flowables.append(title_text)
    
    body = [
    f"Dear {candidate_data['name']},",	
    "Congratulation!",
    f"We are pleased to offer you a position of <b>{candidate_data['designation']}</b> in <b>{candidate_data['unit']},</b> T.K. Bhaban ({candidate_data['location']} floor), 13 Kawran Bazar, Dhaka-1215 based on interview and discussion you had with us.",
    f"Your appointment will be effective on or before <b>{candidate_data['joining_date'].strftime('%d-%b-%Y')}</b>. Please contact us immediately if you require an alternative joining date. If you do not confirm your acceptance or we are unable to set an alternative date, this offer will be withdrawn.",
    "<br/>",
    "Please collect the appointment letter and report on the joining date at 9:00 a.m.",
    "On your joining date, please bring the following documents:",
    """
    <para leftIndent='25'> 
    • This Offer Letter <br/>
    • Two copies of color photograph (passport size) <br/>
    • All academic certificates with a set of photocopies <br/>
    • <u>Resignation Acceptance and Clearance Letter</u> from your most recent employer <br/>
    • TIN Certificate <br/>
    • Last month’s Pay Certificate.
    </para>
    """
]


    normal_style.alignment = 4 

    for line in body:
        flowables.append(Paragraph(line, normal_style))
        flowables.append(Spacer(1, 0.1 * inch))

    flowables.append(Paragraph(" <strong>*	Please note that all the above documents are mandatory.</strong>", normal_style))
    flowables.append(Spacer(2, 0.1 * inch))
    
    
    signature =[
        """<b>
        <br/>
        <br/>
        _____________________________________ <br/>
        Col Almas Raisul Ghani, psc, G (Retd) <br/>						                             
        Director, HR & OD <br/>
        T.K. Group <br/>
        </b>
"""

    ]
    

    for line in signature:
        flowables.append(Paragraph(line, normal_style))
        flowables.append(Spacer(1, 0.1 * inch))

        
    doc = SimpleDocTemplate(pdf_file, pagesize=letter)
    doc.build(flowables, onFirstPage=lambda canvas, doc: onfirstpage(canvas, doc, candidate_data))

  
def onfirstpage(canvas, doc, candidate_data):
    styles = getSampleStyleSheet()
    styleN = styles['Normal']
    styleH = styles['Title']
    styleH.fontSize = 12
    styleH.fontName = "Times-Roman"
    styleN.fontName = "Times-Roman"
    styleN.fontSize = 12
    styleN.alignment = 4 
    flowables = []
    #add some flowables
    flowables.append(Paragraph("<b><u>Accepted</u></b>", styleH))
    flowables.append(Paragraph(
                                f"""I, {candidate_data['name']}, confirm acceptance of your offer of employment based on 
                               the terms and conditions contained herein above which I have read and understood. 
                               <br/> <br/>Signature: _________________________&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                               &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                               Date: ___________________""",
                               styleN
                               )
                     )
    flowables.append(Spacer(1, 0.1 * inch))
    f = Frame(1.1*inch, .9*inch, 6.5*inch, 1.4*inch, showBoundary=1)
    f.addFromList(flowables, canvas)
        

