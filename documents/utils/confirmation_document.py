from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Frame, PageBreak, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import os
from dateutil.relativedelta import relativedelta

def confirm_appraisal_paper(employee_date, pdf_file):
    flowables = []
    styles = getSampleStyleSheet()

    # Configure paragraph styles
    title_style = ParagraphStyle(
        name='TitleStyle',
        fontName="Times-Bold",
        fontSize=14,
        leading=14,
        textColor=colors.black,
        alignment=1,  # Center alignment
    )

    normal_styles = styles['Normal']
    normal_styles.fontName = "Times-Roman"
    normal_styles.fontSize = 11
    normal_styles.alignment = 4 
    
    # Add header paragraph
    header = "<u>Performance Appraisal for Probationary Employee</u>"
    flowables.append(Paragraph(header, title_style))
    flowables.append(Spacer(1, 15))

    # Define the table data
    emp_info_table = [
        [f"Name of Employee: {employee_date['name']}", ""],
        [f'Designation: {employee_date['designation']}', f'Employee ID: {employee_date['EID']}'],
        [f'Department: {employee_date["department"]}', f'Unit: {employee_date['unit']}'],
        [f'Job Location: {employee_date['location']}', ''],
        [f'Joining date: {employee_date['joining_date'].strftime("%d-%b-%Y")}', \
        f'Confirmation due date: {employee_date['confirmation_date'].strftime("%d-%b-%Y")}'], 
    ]


    col_widths = [3.5 * inch, 3.28* inch] 
    emp_info_row_heights = [0.4 * inch] * len(emp_info_table)
    

    t = Table(emp_info_table, colWidths=col_widths, rowHeights=emp_info_row_heights)

    LIST_STYLE = TableStyle(
        [   ('SPAN', (0,0), (-1,0)),
            ('SPAN', (0,3), (-1,3)),
            ('GRID', (0, 0), (-1, -1), .5, colors.black),
            ('LINEABOVE', (0, 0), (-1, 4), .5, colors.black),
            ('LINEBELOW', (0, -1), (-1, -1), .5, colors.black),
            ('ALIGN', (1, 0), (1, 4), 'LEFT'),
            ('VALIGN', (0, 0), (-1, 4), 'MIDDLE'), 
            ('FONT', (0, 0), (-1, -1), 'Times-Bold')
        ]
    )
    t.setStyle(LIST_STYLE)
    flowables.append(t)
    flowables.append(Spacer(1,15))
    
    text = "(Immediate supervisor will put (√) in the following table and complete the appraisal)"
    flowables.append(Paragraph(text, normal_styles))
    flowables.append(Spacer(1,10))
    
    
    rating_data = [
        ['Subject', 'Outstanding\n(5)', 'Very Good\n(4)', 'Good\n(3)', 'Average\n(2)', 'Poor\n(1)'],
        ['Job Performances', '','','','','\n'],
        ['Keenness to Learn', '','','','','\n'],
        ['Interpersonal Skills', '','','','','\n'],
        ['Attitude', '','','','','\n'],
        ['Commitment', '','','','','\n'],
        ['Total marks obtained (Out of 25):', '','Obtained marks in %:','','','\n'],
        ['Strengths:\n\n\n\n\n\n', '','Areas of development:\n\n\n\n\n\n','','',''],
        ['Recommendation & Signature of Immediate supervisor:\n\n\n\n\n', '','Departmental Recommendation & Signature:\n\n\n\n\n','','',''],
    ]
    
    rating_col_widths = [2.75* inch] + [.8 * inch] * 5 
    rating_table = Table(rating_data, colWidths=rating_col_widths)

    LIST_STYLE_RATING = TableStyle(
        [
            ('SPAN', (0, 6), (1, 6)),
            ('SPAN', (0, 7), (1, 7)),
            ('SPAN', (0, 8), (1, 8)),
            ('SPAN', (2, 6), (-1, 6)),
            ('SPAN', (2, 7), (-1, 7)),
            ('SPAN', (2, 8), (-1, 8)),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('LINEABOVE', (0, 0), (-1, 0), 0.5, colors.black), 
            ('LINEBELOW', (0, -1), (-1, -1), 0.5, colors.black), 
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'), 
            ('ALIGN', (2, 6), (-1, -1), 'LEFT'), 
            ('VALIGN', (0, 0), (-1, 6), 'MIDDLE'), 
            ('FONT', (0, 0), (-1, -1), 'Times-Bold'),  
      ]
    )
    
    rating_table.setStyle(LIST_STYLE_RATING)
    flowables.append(rating_table)
    flowables.append(Spacer(1,10))
    
    direction_approval = [
        ['Final Approval', ""],
        ['Comments and Signature of Director:\n\n\n\n\n', 'Comments and Signature of HR Head:\n\n\n\n\n'],
     
    ]
    director_col_widths = [3.5 * inch, 3.28* inch] 
    
    director_approval_table = Table(direction_approval, colWidths=director_col_widths)
    
    LIST_STYLE_DIRECTOR_APPROVAL = TableStyle(
        [
            ('SPAN', (0,0), (-1,0)),
            ('ALIGN', (0,0), (-1,0), "CENTER"),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('LINEABOVE', (0, 0), (-1, 0), 0.5, colors.black), 
            ('LINEBELOW', (0, -1), (-1, -1), 0.5, colors.black), 
            ('FONT', (0, 0), (-1, -1), 'Times-Bold'), 
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey), 
      ]
    )
    
    director_approval_table.setStyle(LIST_STYLE_DIRECTOR_APPROVAL)
    flowables.append(director_approval_table)


    doc = SimpleDocTemplate(pdf_file, pagesize=letter, bottomMargin=0*inch)
    doc.build(flowables, onFirstPage=onfirstpage)

    
def onfirstpage(canvas, doc):
    settings_dir = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.dirname(settings_dir))
    logo_path = os.path.join(project_root, 'logo.png')
    styles = getSampleStyleSheet()

    ref_style = ParagraphStyle(
        name='sub_normal_style',
        fontName="Times-Italic",
        fontSize=9,
        leading=14,
        textColor=colors.black,  
    )
    ref_frame = Frame(6*inch, 9.7*inch, 4*inch, .5*inch, showBoundary=0)
    ref_frame.addFromList([Paragraph("Form: PAP/01-2019 (Annexure – J)", ref_style)],canvas)
    
    canvas.drawImage(logo_path, 280, 730, width=48.62, height=58.32, mask='auto')
    
    
def confirmation_letter(employee_data, pdf_file):
    flowables = []
    styles = getSampleStyleSheet()

    # Configure paragraph styles
    body_style = ParagraphStyle(
        name='TitleStyle',
        fontName="Times-Roman",
        fontSize=11,
        leading=14,
        textColor=colors.black,
        alignment=4,  # Center alignment
    )

    normal_styles = styles['Normal']
    normal_styles.fontName = "Times-Roman"
    normal_styles.fontSize = 11
    normal_styles.alignment = 4
    # Add header paragraph
    header = f"""
    <br/><br/><br/><br/>
    {employee_data['ref']}<br/>
    {employee_data['issue_date'].strftime("%d-%b-%Y")}<br/><br/>								           

    <b>{employee_data['name']}</b><br/>
    <b>Employee ID: {employee_data['EID']}</b><br/>
   {employee_data['designation']}<br/><br/><br/><br/>
    
    <b>Subject: Letter of Confirmation.</b><br/><br/><br/>
    Dear Mr. {employee_data['name']},


    """
    flowables.append(Paragraph(header, normal_styles))
    flowables.append(Spacer(1, 15))
    
    body_text = f"""
    
    Referring to your performance on the current work during the probation period, 
    Management of the company is pleased to confirm your appointment as <b>{employee_data['new_designation']}</b> with effect from <b>{employee_data['effective_date'].strftime("%d-%b-%Y")}</b>.<br/>
    """
    
    flowables.append(Paragraph(body_text, body_style))
    flowables.append(Spacer(1, 15))
    
    if employee_data['development_area'] != "":
        
        body_text_2 =f"""{employee_data['development_area']}<br/><br/>  

            All other terms and conditions of your employment remain unchanged.<br/> <br/>

            We hope that, you will continue to contribute your best effort at all times for the development of company.<br/> <br/> <br/> <br/> 
    """
    else:
        body_text_2 =f"""

            All other terms and conditions of your employment remain unchanged.<br/> <br/>

            We hope that, you will continue to contribute your best effort at all times for the development of company.<br/> <br/> <br/> <br/> 

    """
    flowables.append(Paragraph(body_text_2, body_style))
    flowables.append(Spacer(1, 15))
        
    
    
    signature_text = f"""
        <b>__________________________________</b><br/> 				
        <b>Col Almas Raisul Ghani, psc, G (Retd)</b><br/> 						                             
        <b>Director, HR & OD</b><br/> 
        <b>T.K. Group</b><br/> <br/> <br/> <br/> 

        Cc:<br/> 								
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{employee_data['business_director']}<br/>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Head of Business<br/> 
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Accounts Department<br/>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Personal files<br/> 
    """
    flowables.append(Paragraph(signature_text, normal_styles))
    flowables.append(Spacer(1, 15))
    doc = SimpleDocTemplate(pdf_file, pagesize=letter, bottomMargin=0*inch)
    doc.build(flowables)


def extension_letter(employee_data, pdf_file):
    flowables = []
    styles = getSampleStyleSheet()

    # Configure paragraph styles
    body_style = ParagraphStyle(
        name='TitleStyle',
        fontName="Times-Roman",
        fontSize=11,
        leading=14,
        textColor=colors.black,
        alignment=4,  # Center alignment
    )

    normal_styles = styles['Normal']
    normal_styles.fontName = "Times-Roman"
    normal_styles.fontSize = 11
    normal_styles.alignment = 4
    # Add header paragraph
    header = f"""
    <br/><br/><br/><br/>
   {employee_data['ref']}<br/>
    {employee_data['issue_date'].strftime("%d-%b-%Y")}<br/><br/>								           

    <b>{employee_data['name']}</b><br/>
    <b>Employee ID: {employee_data['EID']}</b><br/>
   {employee_data['designation']}<br/><br/><br/><br/>

    
    <b>Subject: Extension of Probation period.</b><br/><br/><br/>
    Dear Mr. {employee_data['name']},


    """
    flowables.append(Paragraph(header, normal_styles))
    flowables.append(Spacer(1, 15))
    
    body_text = f"""
    
    Referring to your presentation on the current work summary during probation period, Management has decided to extend your probation 
    period for 3 (three) more months with effect from <b>{employee_data['effective_date'].strftime("%d-%b-%Y")}</b>. 
    <br/><br/>{employee_data['development_area']}

    <br/><br/>All other terms and conditions of your employment remain unchanged.

    <br/><br/>We hope that you will continue to contribute your best effort at all times for development of the company.

    <br/><br/><u><b>For Consumer division only:</b></u> You are requested to forward Subject Report by <b>{(employee_data['effective_date']+relativedelta(months=3, days=15)).strftime("%d-%b-%Y")}</b> positively to HRD.

    """
    flowables.append(Paragraph(body_text, body_style))
    flowables.append(Spacer(1, 15))
    
    signature_text = f"""
        <br/><br/><b>__________________________________</b><br/> 				
        <b>Col Almas Raisul Ghani, psc, G (Retd)</b><br/> 						                             
        <b>Director, HR & OD</b><br/> 
        <b>T.K. Group</b><br/> <br/> <br/> <br/> 

        Cc:<br/> 								
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{employee_data['business_director']}<br/>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Head of Business<br/> 
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Accounts Department<br/>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Personal files<br/> 
    """
    flowables.append(Paragraph(signature_text, normal_styles))
    flowables.append(Spacer(1, 15))
    doc = SimpleDocTemplate(pdf_file, pagesize=letter, bottomMargin=0*inch)
    doc.build(flowables)
