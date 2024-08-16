from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Frame, PageBreak
from reportlab.lib.units import inch
from reportlab.lib import colors
import os


def create_joining_form(employee_data, pdf_file):
    # Create a list to hold the flowable objects
    flowables = []

    # Define styles
    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    normal_style = styles["Normal"]
    normal_style.leading = 15
    styles["Normal"].fontName = "Times-Roman"
    styles["Normal"].fontSize  = 11
    title_style.fontName = "Times-Roman"
    title_style.fontsize = 14
    normal_style.alignment = 4 

    header = [
            f"Date: <b>{employee_data['doj'].strftime('%d-%b-%y')}</b>",
            "To",
            "Director, HR & Admin",
            "T.K. Group",
            "<br/>"
            "<b><u>Subject: Joining Report</u><br/></b>"
    ]
    
    for line in header:
        flowables.append(Paragraph(line,normal_style))
        
    body =[
        "<br/>",
        "<br/>Dear Sir<br/><br/>",
        f"""With reference to the Appointment Letter/ Offer Letter issued to me dated <b><u>{employee_data['doj'].strftime('%d-%b-%y')}</u></b>,
            I am pleased to join today <b><u>{employee_data['doj'].strftime('%d/%m/%y')}</u></b> 
            at 9:00 AM as <b><u>{employee_data["designation"]}</u></b> in the <b><u>{employee_data["dept"]}</u></b>
            department of <b><u>{employee_data['company']}</u></b>. Necessary papers are enclosed herewith.
            Please accept my joining in your esteemed organization and oblige thereby.""",
        "<br/>I look forward to your cooperation and necessary orientation for a good start in the said position.",
        "<br/>Thank you.",
        "<br/>Sincerely yours,<br/><br/>",
        f"""       
        ___________________<br/>
        Signature with Date<br/><br/>
        Name: <b>{employee_data['name']}</b><br/><br/><br/>
        <b><u>Enclosure (Put √):</u></b><br/><br/>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    1.&nbsp;&nbsp;Personal Information Form<br/>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    2.&nbsp;&nbsp;ID Card Requisition Form<br/>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    3.&nbsp;&nbsp;Benevolent Fund Application Form<br/>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    4.&nbsp;&nbsp;Photocopy of NID/ Passport/ ……………………<br/>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    5.&nbsp;&nbsp;Passport size photo<br/>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    6.&nbsp;&nbsp;Educational, Experience and Training Certificates with photocopy<br/>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    7.&nbsp;&nbsp;TIN Certificate<br/>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    8.&nbsp;&nbsp;Release Letter from Previous Employer (If Applicable)<br/>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    9.&nbsp;&nbsp;NID photocopy and photo of Nominee<br/>
        &nbsp;&nbsp;&nbsp;&nbsp;          10.&nbsp;&nbsp;NID photocopy and photo of References<br/>
        &nbsp;&nbsp;&nbsp;&nbsp;          11.&nbsp;&nbsp;Medical Certificate<br/>
        &nbsp;&nbsp;&nbsp;&nbsp;          12.&nbsp;&nbsp;Agreement Copy<br/>
		"""					
    ]

    for line in body:
        flowables.append(Paragraph(line, normal_style))
        
    flowables.append(PageBreak())
    flowables.append(Paragraph("",normal_style))
    
    
    
    doc = SimpleDocTemplate(pdf_file, pagesize=letter)
    doc.build(flowables, onFirstPage=onfirstpage, onLaterPages=lambda canvas, doc: onlaterpage(canvas, doc, employee_data))
 
    
def onfirstpage(canvas, doc):
    settings_dir = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.dirname(settings_dir))
    logo_path = os.path.join(project_root, 'logo.png')
    styles = getSampleStyleSheet()
    normal_style = styles["Normal"]
    normal_style.leading = 15
    normal_style.fontName = "Times-Roman"
    normal_style.fontSize  = 11
    normal_style.alignment = 1 
    flowables = []
    #add some flowables
    flowables.append(Paragraph(
                                """
                                ________________<br/>
                                  &nbsp; HR Endorsement<br/><br/><br/><br/><br/><br/>
                                ______________________________<br/>
                                 Acceptance of Reporting Manager<br/>
                                """,
                               normal_style
                               )
                     )
    canvas.drawImage(logo_path, 280, 730, width=48.62, height=58.32, mask='auto')
    flowables.append(Spacer(1, 0.1 * inch))
    f = Frame(5*inch, .5*inch, 3.4*inch, 5.7*inch, showBoundary=0)
    f.addFromList(flowables[:], canvas)

  
def onlaterpage(canvas, doc,employee_data):
    settings_dir = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.dirname(settings_dir))
    logo_path = os.path.join(project_root, 'logo.png')
    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    title_style.fontName = "Times-Roman"
    title_style.fontSize = 10
    normal_style = styles["Normal"]
    normal_style.leading = 15
    normal_style.fontName = "Times-Roman"
    normal_style.fontSize  = 11
    normal_style.alignment = 1 
    
    sub_normal_style = ParagraphStyle(
        name= 'sub_normal_style',
        fontName = "Times-Roman",
        fontSize = 11,
        leading = 20,
    )
    
    sub_E_normal_style = ParagraphStyle(
        name= 'sub_normal_style',
        fontName = "Times-Roman",
        fontSize = 11,
        leading = 14,
    )
    

    
    body_normal_style = ParagraphStyle(
        name= 'body_normal_style',
        fontName = "Times-Roman",
        fontSize = 11,
        leading = 13,
    )
    
    flowables = []
    other_text = []
    #add some flowables
    
    flowables.append(Paragraph("Employee’s Photo", normal_style))
    flowables.append(Spacer(1, 0.1 * inch))
    f = Frame(7*inch, 9.2*inch, 1.34*inch, 1.56*inch, showBoundary=1)
    other_text.append(Paragraph("<b>Personal Information</b>", normal_style))
    
    g = Frame(.6*inch, 8.8*inch, 7*inch, .25*inch, topPadding=0, bottomPadding=0, showBoundary=1)
    titleF = Frame(.1*inch, 9.3*inch, 8*inch, .7*inch, topPadding=0, bottomPadding=0, showBoundary=0)
    nameF = Frame(.6*inch, 8.5*inch, 7*inch, .25*inch, topPadding=0, bottomPadding=0, showBoundary=0)
    FnameF = Frame(.6*inch, 6.5*inch, 7*inch, 2*inch, topPadding=0, bottomPadding=0, showBoundary=0)
    MnameF = Frame(.6*inch, 4.5*inch, 7*inch, 2*inch, topPadding=0, bottomPadding=0, showBoundary=0)
    SnameF = Frame(.6*inch, 2.5*inch, 7*inch, 2*inch, topPadding=0, bottomPadding=0, showBoundary=0)
    PaddresssF = Frame(.6*inch, 1.9*inch, 7*inch, .6*inch, topPadding=0, bottomPadding=0, showBoundary=0)
    mailaddresssF = Frame(.6*inch, 1.28*inch, 7*inch, .6*inch, topPadding=0, bottomPadding=0, showBoundary=0)
    peraddresssF = Frame(.6*inch, 0.65*inch, 7*inch, .6*inch, topPadding=0, bottomPadding=0, showBoundary=0)
    PassportF  = Frame(.6*inch, 0.30*inch, 7*inch, .3*inch, topPadding=0, bottomPadding=0, showBoundary=0)
    rightSideF = Frame(4.1*inch, 2.5*inch, 3.5*inch, 6*inch, topPadding=0, bottomPadding=0, showBoundary=0)
    

    
    
    canvas.saveState()
    canvas.setFillColor(colors.lightgrey)
    canvas.rect(.6*inch, 8.8*inch, 7*inch, .25*inch, fill=1)
    canvas.restoreState()
    f.addFromList(flowables, canvas)
    g.addFromList(other_text,canvas)
    titleF.addFromList([Paragraph("<br/><b><u>EMPLOYEE INFORMATION FORM (EIF)</u></b>", title_style)], canvas)
    
    nameF.addFromList([Paragraph(f"<b>Full Name: {employee_data['name']}</b>", body_normal_style)], canvas)
    
    # Fathers Informaiton
    FnameF.addFromList([Paragraph(f"""
                                  <b>Father's Name: {employee_data['father_name']}</b><br/><br/> 
                                  Profession: <br/><br/>
                                  Organization & Address:<br/><br/>
                                  Contact No:<br/><br/>
                                  NID No:<br/>
                                  (Attached the photocopy of NID)
                                
                                  """, body_normal_style)], canvas)
    # Mothers Informaiton
    MnameF.addFromList([Paragraph(f"""
                                  <b>Mother's Name: {employee_data['mother_name']}</b><br/><br/> 
                                  Profession: <br/><br/>
                                  Organization & Address:<br/><br/>
                                  Contact No:<br/><br/>
                                  NID No:<br/>
                                  (Attached the photocopy of NID)
                                
                                  """, body_normal_style)], canvas)
    
    SnameF.addFromList([Paragraph(f"""
                                  <b>Spouse Name: {employee_data['spouse_name']} </b><br/><br/> 
                                  Profession: <br/><br/>
                                  Organization & Address:<br/><br/>
                                  Contact No:<br/><br/>
                                  NID No:<br/>
                                  (Attached the photocopy of NID)
                                
                                  """, body_normal_style)], canvas)
    
    PaddresssF.addFromList([Paragraph(f"""
                                  <b>Present Address: {employee_data['present_address']}</b><br/>

                                Name & Contact No. of house owner:
                                
                                  """, body_normal_style)], canvas)
    
    mailaddresssF.addFromList([Paragraph("""
                                  <b>Mailing Address:</b><br/><br/>

                                Name & Contact No. of Local Representative:
                                
                                  """, body_normal_style)], canvas)
    
    peraddresssF.addFromList([Paragraph(f"""
                                <b>Permanent Address: {employee_data['permanent_address']}</b><br/><br/>

                                Name & Contact No. of Local Representative:
                                
                                  """, body_normal_style)], canvas)
    peraddresssF.addFromList([Paragraph("""
                                <b>Permanent Address:</b><br/><br/>

                                Name & Contact No. of Local Representative:
                                
                                  """, body_normal_style)], canvas) 
    
    PassportF.addFromList([Paragraph("""
                                Passport Details (If any):  Number: ……………………………….        Date of Issue: …………………
                                
                                  """, body_normal_style)], canvas)
    
    rightSideF.addFromList([Paragraph(f"""
                                    <br/>    
                                    Sex: M / F <br/><br/>

                                    Marital Status: Married/ Unmarried<br/><br/>

                                    Personal Contact Numbers: {employee_data['personal_mobile_no']} <br/><br/>

                                    Official Contact Number:<br/><br/>                              

                                    Religion:  {employee_data['religion']}<br/><br/>

                                    Nationality: Bangladeshi <br/><br/>

                                    Blood Group: {employee_data['blood_group']} <br/><br/>

                                    National ID No.: {employee_data['NID']}<br/><br/>

                                    TIN (Mandatory): {employee_data['tin']} <br/><br/>

                                    Date of Birth: {employee_data['dob']} <br/><br/>

                                    Place Of Birth: <br/><br/>

                                    Personal e-mail Address: {employee_data['personal_email']} <br/><br/><br/>

                                    Official e-mail Address:<br/><br/>


                                    Number of Children (if any):<br/><br/><br/>

                                    No. Boys: {employee_data['son']}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;No. Girls: {employee_data['daughter']}

                                
                                  """, body_normal_style)], canvas)           
   
    canvas.drawImage(logo_path, 280, 730, width=48.62, height=58.32, mask='auto')
    canvas.line(43, 633, 43, 20)#horizontal line
    canvas.line(43, 45, 547, 45) #bottom line
    canvas.line(547, 633, 547, 20) #right side horizontal line
    canvas.line(43, 613, 547, 613) #under full name
    canvas.line(43, 470, 294, 470) #half Line
    canvas.line(294, 613, 294, 180) # middle line
    canvas.line(43, 325, 294, 325) #Above Spouse line
    canvas.line(43, 180, 547, 180) #under spouse line
    canvas.line(43, 135, 547, 135) #under Present Address line
    canvas.line(43, 90, 547, 90) #under Mailing Address line
    canvas.line(43, 20, 547, 20)#bottom line
    
    #Third Page
    
    canvas.showPage()
    canvas.drawImage(logo_path, 280, 730, width=48.62, height=58.32, mask='auto')
    thirdF = Frame(.7*inch, 5*inch, 7*inch, 5*inch, topPadding=0, bottomPadding=0, showBoundary=1)
    Emgency_ref_F = Frame(.7*inch, 7.75*inch, 3.55*inch, 2*inch, topPadding=0, bottomPadding=0, showBoundary=0)
    Emgency_ref__r_F = Frame(4.25*inch, 7.75*inch, 3.47*inch, 2*inch, topPadding=0, bottomPadding=0, showBoundary=0)
    referance_F = Frame(.7*inch, 4.95*inch, 3.55*inch, 3*inch, topPadding=0, bottomPadding=0, showBoundary=0)
    referance_r_F = Frame(4.25*inch, 4.95*inch, 3.55*inch, 3*inch, topPadding=0, bottomPadding=0, showBoundary=0)
    education_F = Frame(.7*inch, 2.85*inch, 7*inch, 2*inch, topPadding=0, bottomPadding=0, showBoundary=1)
    education_degree_F = Frame(.7*inch, 3.9*inch, 3.5*inch, .7*inch, topPadding=0, bottomPadding=0, showBoundary=0)
    education_degree__r_F = Frame(4.25*inch, 3.9*inch, 3.5*inch, .7*inch, topPadding=0, bottomPadding=0, showBoundary=0)
    Pro_education_degree_F = Frame(.7*inch, 3.6*inch, 3.5*inch, .5*inch, topPadding=0, bottomPadding=0, showBoundary=0)
    Pro_education_degree__r_F = Frame(4.25*inch, 3.4*inch, 3.5*inch, .6*inch, topPadding=0, bottomPadding=0, showBoundary=0)
    Training_education_degree_F = Frame(.7*inch, 2.85*inch, 3.5*inch, .5*inch, topPadding=0, bottomPadding=0, showBoundary=0)
    Training_education_degree__r_F = Frame(4.25*inch, 2.80*inch, 3.5*inch, .6*inch, topPadding=0, bottomPadding=0, showBoundary=0)
    
    exprienance_F = Frame(.7*inch, 0.1*inch, 7*inch, 2.6*inch, topPadding=0, bottomPadding=0, showBoundary=1)
    first_exp_left_F = Frame(.8*inch, 1*inch, 3.5*inch, 1.5*inch,rightPadding=0,leftPadding=0, topPadding=0, bottomPadding=0, showBoundary=0)
    first_exp_right_F = Frame(4.30*inch, 1*inch, 3.5*inch, 1.5*inch,rightPadding=0,leftPadding=0, topPadding=0, bottomPadding=0, showBoundary=0)
    second_exp_left_F = Frame(.8*inch, 0.1*inch, 3.5*inch, 1.2*inch,rightPadding=0,leftPadding=0, topPadding=0, bottomPadding=0, showBoundary=0)
    second_exp_right_F = Frame(4.30*inch, 0.1*inch, 3.5*inch, 1.2*inch,rightPadding=0,leftPadding=0, topPadding=0, bottomPadding=0, showBoundary=0)

    
  
    
    canvas.saveState()
    canvas.setFillColor(colors.lightgrey)
    canvas.rect(.7*inch, 9.8*inch, 7*inch, .20*inch, fill=1)
    canvas.restoreState()
    thirdF.addFromList([Paragraph("""
                                <b>Emergency Contact Information</b>
                                
                                  """, normal_style)], canvas)
    
    
    Emgency_ref_F.addFromList([Paragraph(f"""
                                1. Name: {employee_data['emergency_contact_person']}<br/>
                                  Address: {employee_data['emergency_contact_address']}<br/>

                                  Relation: {employee_data['emer_relation_with_employee']}<br/>
                                  Contact No: {employee_data['emergency_contact_no']}<br/>
                                  Alternative Contact No:<br/>
                                
                                  """, sub_normal_style)], canvas)
    Emgency_ref__r_F.addFromList([Paragraph("""
                                2. Name:<br/>
                                  Address:<br/><br/>

                                  Relation:<br/>
                                  Contact No:<br/>
                                  Alternative Contact No:<br/>                                
                                  """, sub_normal_style)], canvas)
    
    referance_F.addFromList([Paragraph("""
                                <b><u>Reference (1):</u></b><br/>
                                Name:<br/>
                                Address:<br/>
                                Organization:<br/>
                                Designation:<br/>
                                Contact No:<br/>
                                Relation:<br/>
                                Signature:_________<br/>
                                (Attached NID photocopy & one passport size photo) 
                               
                                  """, sub_normal_style)], canvas)
    
    referance_r_F.addFromList([Paragraph("""
                                <b><u>Reference (2):</u></b><br/>
                                Name:<br/>
                                Address:<br/>
                                Organization:<br/>
                                Designation:<br/>
                                Contact No:<br/>
                                Relation:<br/>
                                Signature:_________<br/>
                                (Attached NID photocopy & one passport size photo) 
                               
                                  """, sub_normal_style)], canvas)

    
    canvas.saveState()
    canvas.setFillColor(colors.lightgrey)
    canvas.rect(.7*inch, 4.65*inch, 7*inch, .20*inch, fill=1)
    canvas.restoreState()
    
    education_F.addFromList([Paragraph("""
                                <b>Educational Background</b>
                               
                                  """, normal_style)], canvas)
    education_degree_F.addFromList([Paragraph(f"""
                                Highest Educational Degree: {employee_data['highest_education']}
                               
                                  """, sub_normal_style)], canvas)
    
    education_degree__r_F.addFromList([Paragraph(f"""
                                Institution: {employee_data['high_institution']}<br/>
                                Year: {employee_data['passing_year']}                           

                                  """, sub_normal_style)], canvas)
    Pro_education_degree_F.addFromList([Paragraph(f"""
                                    Professional / Additional Qualification: {employee_data['professional_degree']}
                               
                                  """, sub_normal_style)], canvas)
    Pro_education_degree__r_F.addFromList([Paragraph(f"""
                                    Institution: {employee_data['pro_institution']}<br/>
                                    Year: {employee_data['pro_passing_year']}                                                             
                                  """, sub_normal_style)], canvas)
    Training_education_degree_F.addFromList([Paragraph("""
                                    Latest Training:
                               
                                  """, sub_normal_style)], canvas)
    Training_education_degree__r_F.addFromList([Paragraph("""
                                    Duration: <br/>
                                    Year                             
                                  """, sub_normal_style)], canvas)
    
    canvas.saveState()
    canvas.setFillColor(colors.lightgrey)
    canvas.rect(.7*inch, 2.5*inch, 7*inch, .20*inch, fill=1)
    canvas.restoreState()
    
    exprienance_F.addFromList([Paragraph("""
                                <b>Information of previous job (if any)</b>
                               
                                  """, normal_style)], canvas)
    
    first_exp_left_F.addFromList([Paragraph("""
                                1) Organization Name & Address:<br/><br/><br/><br/>
                                Duration:<br/>
                                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;From: .................&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;To: .....................
                               
                                  """, sub_E_normal_style)], canvas)
    first_exp_right_F.addFromList([Paragraph("""
                                Designation:<br/><br/>
                                Department:<br/><br/>
                                Referrence Name & Contact Number:
                              
                                """, sub_E_normal_style)], canvas)
    
    second_exp_left_F.addFromList([Paragraph("""
                                2) Organization Name & Address:<br/><br/><br/><br/>
                                Duration:<br/>
                                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;From: .................&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;To: .....................
                               
                                  """, sub_E_normal_style)], canvas)
    second_exp_right_F.addFromList([Paragraph("""
                                Designation:<br/><br/>
                                Department:<br/><br/>
                                Referrence Name & Contact Number:
                              
                                """, sub_E_normal_style)], canvas)
  
    canvas.line(4.25*inch, 9.8*inch, 4.25*inch, 5*inch) # middle line emergency
    canvas.line(.7*inch,  9.8*inch, 7.7*inch, 9.8*inch) 
    canvas.line(.7*inch, 8*inch, 7.7*inch, 8*inch) # under Engency line
    canvas.line(.7*inch, 4.65*inch, 7.7*inch, 4.65*inch) # under Engency line
    canvas.line(4.25*inch, 4.65*inch, 4.25*inch, 2.85*inch)# middle line education
    canvas.line(.7*inch, 4.1*inch, 7.7*inch, 4.1*inch) # under Engency line
    canvas.line(.7*inch, 3.5*inch, 7.7*inch, 3.5*inch) # under Engency line
    canvas.line(.7*inch, 2.5*inch, 7.7*inch, 2.5*inch)
    canvas.line(4.25*inch, 2.5*inch, 4.25*inch, .1*inch)# middle line Education
    
    #1st exprienance
    canvas.line(4.25*inch, 2.1*inch, 7.7*inch, 2.1*inch)
    canvas.line(.7*inch, 1.8*inch, 7.7*inch, 1.8*inch)
    canvas.line(.7*inch, 1.3*inch, 7.7*inch, 1.3*inch)
    #2nd exprienance
    canvas.line(4.25*inch, .95*inch, 7.7*inch, .95*inch)
    canvas.line(.7*inch, .6*inch, 7.7*inch, .6*inch)
    # canvas.line(.7*inch, 1.2*inch, 7.7*inch, 1.2*inch)
    canvas.showPage()
    canvas.drawImage(logo_path, 280, 730, width=48.62, height=58.32, mask='auto')
    titleF = Frame(.7*inch, 9.3*inch, 7*inch, .7*inch, topPadding=0, bottomPadding=0, showBoundary=0)
    text_f = Frame(.7*inch, 8.6*inch, 7*inch, .7*inch, topPadding=0, bottomPadding=0, showBoundary=0)
    nominee_f = Frame(.7*inch, 6.63*inch, 7*inch, 2.3*inch, topPadding=0, bottomPadding=0, showBoundary=1)
    nominee_info_f = Frame(.7*inch, 6.63*inch, 5.3*inch, 2.3*inch, topPadding=0, bottomPadding=0, showBoundary=0)
    photo_f = Frame(5.8*inch, 6.75*inch, 1.9*inch, 1.2*inch, topPadding=0, bottomPadding=0, showBoundary=0)
    more_nominee_F = Frame(.7*inch, 5.9*inch, 7*inch, .7*inch, topPadding=0, bottomPadding=0, showBoundary=0)
    ack_nominee_F = Frame(.7*inch, 5.6*inch, 7.2*inch, .7*inch, topPadding=0, bottomPadding=0, showBoundary=0)
    
    signature_f = Frame(.7*inch, 5.2*inch, 2*inch, .5*inch, topPadding=0, bottomPadding=0, showBoundary=1)
    signat_f = Frame(.7*inch, 4.6*inch, 2*inch, .5*inch, topPadding=0, bottomPadding=0, showBoundary=0)
    
    
    canvas.line(5.8*inch, 8.92*inch, 5.8*inch, 6.63*inch)
    
    
    titleF.addFromList([Paragraph("<br/><b><u>NOMINATION DECLARATION:</u></b>", title_style)], canvas)
    text_f.addFromList([Paragraph("<b>In case of my death during the course of employment, all legal dues should pay to my nominee as under.</b>", body_normal_style)], canvas)
    nominee_f.addFromList([Paragraph(f"", sub_normal_style)], canvas)
    nominee_info_f.addFromList([Paragraph(f"""
                                     <b>1. Full Name:</b> {employee_data['nominee_name']}   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>Percent (%):</b> 100%<br/>
                                     <b> Father’s Name:</b> {employee_data['nominee_father']}<br/>  
                                      <b>Mother’s Name: </b>{employee_data['nominee_mother']}<br/>
                                      <b>Permanent Address:</b> {employee_data['nominee_address']}<br/>
                                      <b>Relationship with employee:</b> {employee_data['relation_with_employee']} &nbsp;&nbsp<b>Contact No:</b> {employee_data['nominee_mobile']}<br/>
                                      <b>Signature of nominee:</b> <br/>
                                      <b>NID Number (Please attach a photocopy of NID): </b>{employee_data['nominee_nid']}

                                     
                                     """, sub_normal_style)], canvas)
    
    
    photo_f.addFromList([Paragraph('Nominee’s PP size color photograph', normal_style)], canvas)
    more_nominee_F.addFromList([Paragraph('(In case of more nominee, one can use additional page)', sub_E_normal_style)], canvas)
    ack_nominee_F.addFromList([Paragraph("""
                                         <b>**I hereby declare that the above statements are correct and complete to the best of my knowledge.
                                         Any change of above information, 
                                         including Permanent Address will be intimated to HR Department at the earliest.
                                         </b>
                                         """, body_normal_style)], canvas)
    
    
    signature_f.addFromList([Paragraph('', normal_style)], canvas)
    signat_f.addFromList([Paragraph('<b>Signature of Employee</b>', normal_style)], canvas)
    
    normal_style.fontSize = 12
    
    
    official_f = Frame(.7*inch, 2.1*inch, 7*inch, 2.6*inch, topPadding=0, bottomPadding=0, showBoundary=1)
    official_l_f = Frame(.7*inch, 2.15*inch, 3.5*inch, 2.3*inch, topPadding=0, bottomPadding=0, showBoundary=0)
    official_r_f = Frame(4*inch, 2.15*inch, 7*inch, 2.3*inch, topPadding=0, bottomPadding=0, showBoundary=0)
    family_f = Frame(.7*inch, 2.5*inch, 7*inch, .5*inch, topPadding=0, bottomPadding=0, showBoundary=0)
    family_text_f_1 = Frame(.7*inch, 2.25*inch, 2.56*inch, .5*inch, topPadding=0, bottomPadding=0, showBoundary=0)
    family_text_f_2 = Frame(3.5*inch, 2.25*inch,2.56*inch, .5*inch, topPadding=0, bottomPadding=0, showBoundary=0)
    family_text_f_3 = Frame(5.3*inch, 2.25*inch,2.56*inch, .5*inch, topPadding=0, bottomPadding=0, showBoundary=0)
    family_text_f_4 = Frame(.7*inch, 1.9*inch, 2.56*inch, .5*inch, topPadding=0, bottomPadding=0, showBoundary=0)
    family_text_f_5 = Frame(3.5*inch, 1.9*inch,2.56*inch, .5*inch, topPadding=0, bottomPadding=0, showBoundary=0)
    family_text_f_6 = Frame(5.3*inch, 1.9*inch,2.56*inch, .5*inch, topPadding=0, bottomPadding=0, showBoundary=0)
    
    other_text_f = Frame(.7*inch, 1.4*inch, 7*inch, .5*inch, topPadding=0, bottomPadding=0, showBoundary=1)
    rct_text_f = Frame(1.5*inch, 1.55*inch, .5*inch, .2*inch, topPadding=0, bottomPadding=0, showBoundary=1)
    
    
    
    
    canvas.saveState()
    canvas.setFillColor(colors.lightgrey)
    canvas.rect(.7*inch, 4.45*inch, 7*inch, .25*inch, fill=1)
    canvas.restoreState()
    
    official_f.addFromList([Paragraph('<b>Official Information (HR Use only)</b>', normal_style)], canvas)
    official_l_f.addFromList([Paragraph(f"""
                                      Designation: {employee_data['designation']}<br/><br/>
                                      Joining Date: {employee_data['doj'].strftime('%d-%b-%y')}<br/><br/>
                                      Immediate Supervisor:<br/><br/>
                                      Salary A/C No:

                                      """, sub_E_normal_style)], canvas)
    
    official_r_f.addFromList([Paragraph(f"""
                                      Department: {employee_data['dept']}<br/><br/>
                                      Official ID No: {employee_data['eid']}<br/><br/>
                                      Job Location: <br/><br/>
                                      Bank Name:
                                      """, sub_E_normal_style)], canvas)
    canvas.saveState()
    canvas.setFillColor(colors.lightgrey)
    canvas.rect(.7*inch, 2.75*inch, 7*inch, .25*inch, fill=1)
    canvas.restoreState()
    
    family_f.addFromList([Paragraph("""
                                     Family Member/Close Relative in T.K. Group (if any)
                                      """, sub_normal_style)], canvas)
    family_text_f_1.addFromList([Paragraph("""
                                     Name:
                                      """, sub_normal_style)], canvas)
    family_text_f_2.addFromList([Paragraph("""
                                     Designation:
                                      """, sub_normal_style)], canvas)
    family_text_f_3.addFromList([Paragraph("""
                                     Department:
                                      """, sub_normal_style)], canvas)

    family_text_f_4.addFromList([Paragraph("""
                                     Joining Date:
                                      """, sub_normal_style)], canvas)
    family_text_f_5.addFromList([Paragraph("""
                                     SBU:
                                      """, sub_normal_style)], canvas)
    family_text_f_6.addFromList([Paragraph("""
                                     Job Location:
                                      """, sub_normal_style)], canvas)
    
    
    other_text_f.addFromList([Paragraph("""
                                        <br/>
                                     Endorsed:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;HR Officer: …… &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                                     &nbsp;&nbsp;&nbsp;&nbsp;Checked By ……….  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Director, HR & Admin: ……………
                                      """, body_normal_style)], canvas)
    rct_text_f.addFromList([Paragraph("""
                                        <br/>
                                     """, body_normal_style)], canvas)
    
     
    
    canvas.line(.7*inch, 4.2*inch, 7.7*inch, 4.2*inch)
    canvas.line(.7*inch, 3.8*inch, 7.7*inch, 3.8*inch)
    canvas.line(.7*inch, 3.4*inch, 7.7*inch, 3.4*inch)
    canvas.line(.7*inch, 3*inch, 7.7*inch, 3*inch)
    canvas.line(.7*inch, 2.5*inch, 7.7*inch, 2.5*inch)
    canvas.line(4*inch, 4.46*inch, 4*inch, 3*inch)
    canvas.line(3.5*inch, 2.75*inch, 3.5*inch, 2.1*inch)
    canvas.line(5.2*inch, 2.75*inch, 5.2*inch, 2.1*inch)
    
    # ID Card Requisition Form
    canvas.showPage()
    canvas.drawImage(logo_path, 280, 730, width=48.62, height=58.32, mask='auto')
    idCardtitlef = Frame(.7*inch, 9.5*inch, 7*inch, .5*inch,  topPadding=0, bottomPadding=0, showBoundary=0)
    idCardtitlef.addFromList([Paragraph("""
                                       <b>ID CARD REQUISITION FORM</b>
                                     """, normal_style)], canvas)
    
    FullNameF = Frame(.7*inch, 9.35*inch, 7*inch, .4*inch,  topPadding=0, bottomPadding=0, showBoundary=0)
    FullNameF.addFromList([Paragraph("""
                                       <b>FULL NAME OF EMPLOYEE (in block letter):</b>
                                     """, sub_normal_style)], canvas)
    boxF_1 = Frame(.7*inch, 8.95*inch, 7.5*inch, .6*inch,  topPadding=0, bottomPadding=0, showBoundary=1)
    
    boxF_1.addFromList([Paragraph(" ", sub_normal_style)], canvas)
    canvas.line(.7*inch, 9.25*inch, 8.2*inch, 9.25*inch)
    x=1
    i = 0
    while i <24:
      canvas.line(x*inch, 9.55*inch, x*inch, 8.95*inch)
      x+=.3
      i+=1
      
      
    FathersF = Frame(.7*inch, 8.5*inch, 7*inch, .4*inch,  topPadding=0, bottomPadding=0, showBoundary=0)
    FathersF.addFromList([Paragraph("""
                                       <b>FATHER’S NAME (in block letter):</b>
                                     """, sub_normal_style)], canvas)
    boxF_2 = Frame(.7*inch, 8.1*inch, 7.5*inch, .6*inch,  topPadding=0, bottomPadding=0, showBoundary=1)
    
    boxF_2.addFromList([Paragraph(" ", sub_normal_style)], canvas)
    canvas.line(.7*inch, 8.4*inch, 8.2*inch, 8.4*inch)
    x=1
    i = 0
    while i <24:
      canvas.line(x*inch, 8.7*inch, x*inch, 8.10*inch)
      x+=.3
      i+=1
   
    MothersF = Frame(.7*inch, 7.65*inch, 7*inch, .4*inch,  topPadding=0, bottomPadding=0, showBoundary=0)
    MothersF.addFromList([Paragraph("""
                                       <b>MOTHER’S NAME (in block letter):</b>
                                     """, sub_normal_style)], canvas)
    boxF_3 = Frame(.7*inch, 7.25*inch, 7.5*inch, .6*inch,  topPadding=0, bottomPadding=0, showBoundary=1)
    
    boxF_3.addFromList([Paragraph(" ", sub_normal_style)], canvas)
    canvas.line(.7*inch, 7.55*inch, 8.2*inch, 7.55*inch)
    x=1
    i = 0
    while i <24:
      canvas.line(x*inch, 7.85*inch, x*inch, 7.25*inch)
      x+=.3
      i+=1
     
    
    addressPresent_F = Frame(.7*inch, 6.8*inch, 7*inch, .4*inch,  topPadding=0, bottomPadding=0, showBoundary=0)
    addressPresent_F.addFromList([Paragraph("""
                                       <b>PRESENT/ MAILING ADDRESS:	
                                       &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;		 
                                       &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;		 
                                       &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;		 
                                       &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;		 
                                       &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;		 
                                       &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;		 
                                       
                                       PERMANENT ADDRESS:</b>
                                     """, sub_normal_style)], canvas)
    
    presentaddressboxF = Frame(.7*inch, 5.35*inch, 3.5*inch, 1.5*inch, topPadding=0, bottomPadding=0, showBoundary=1)  
    
    presentaddressboxF.addFromList([Paragraph(f"{employee_data['present_address']}", sub_normal_style)], canvas)
    permanentaddressboxF = Frame(4.2*inch, 5.35*inch, 3.5*inch, 1.5*inch, topPadding=0, bottomPadding=0, showBoundary=1)  
    
    permanentaddressboxF.addFromList([Paragraph(f"{employee_data['permanent_address']}", sub_normal_style)], canvas)

    DOJF = Frame(.7*inch, 4.7*inch, 1.5*inch, .4*inch,  topPadding=0, bottomPadding=0, showBoundary=0)
    DOJF.addFromList([Paragraph("<b>DATE OF BIRTH:</b>", sub_normal_style)], canvas)
    
    DOJboxF_1 = Frame(2.2*inch, 4.85*inch, .7*inch, .3*inch, topPadding=0, bottomPadding=0, showBoundary=1)  
    DOJboxF_1.addFromList([Paragraph("", sub_normal_style)], canvas)
    canvas.line(2.6*inch, 5.15*inch, 2.6*inch, 4.85*inch)
    
    DOJboxF_2 = Frame(3*inch, 4.85*inch, .7*inch, .3*inch, topPadding=0, bottomPadding=0, showBoundary=1)  
    DOJboxF_2.addFromList([Paragraph("", sub_normal_style)], canvas)
    canvas.line(3.35*inch, 5.15*inch, 3.35*inch, 4.85*inch)
    
    DOJboxF_3 = Frame(3.9*inch, 4.85*inch, 1.2*inch, .3*inch, topPadding=0, bottomPadding=0, showBoundary=1)  
    DOJboxF_3.addFromList([Paragraph("", sub_normal_style)], canvas)
    canvas.line(4.14*inch, 5.15*inch, 4.14*inch, 4.85*inch)
    canvas.line(4.45*inch, 5.15*inch, 4.45*inch, 4.85*inch)
    canvas.line(4.80*inch, 5.15*inch, 4.80*inch, 4.85*inch)
    
    
    MaritialF = Frame(5.3*inch, 4.7*inch, 1.7*inch, .4*inch,  topPadding=0, bottomPadding=0, showBoundary=0)
    MaritialF.addFromList([Paragraph("<b>MARITAL STATUS:</b>", sub_normal_style)], canvas)
    Maritialbox = Frame(6.9*inch, 4.85*inch, 1.2*inch, .3*inch, topPadding=0, bottomPadding=0, showBoundary=1)  
    Maritialbox.addFromList([Paragraph(f"{employee_data['maritial_status']}", sub_normal_style)], canvas)
    
    SEXF = Frame(.7*inch, 4.35*inch, 1.5*inch, .4*inch,  topPadding=0, bottomPadding=0, showBoundary=0)
    SEXF.addFromList([Paragraph("<b>SEX:</b>", sub_normal_style)], canvas)
    SEXF_1 = Frame(1.2*inch,4.5*inch, .35*inch, .3*inch, topPadding=0, bottomPadding=0, showBoundary=1)  
    SEXF_1.addFromList([Paragraph("<b>M</b>", sub_normal_style)], canvas)
    SEXF_2 = Frame(1.6*inch, 4.5*inch, .35*inch, .3*inch, topPadding=0, bottomPadding=0, showBoundary=1)  
    SEXF_2.addFromList([Paragraph("<b>F</b>", sub_normal_style)], canvas)
    
    
    BloodF = Frame(5.5*inch, 4.35*inch, 1.7*inch, .4*inch,  topPadding=0, bottomPadding=0, showBoundary=0)
    BloodF.addFromList([Paragraph("<b>BLOOD GROUP:</b>", sub_normal_style)], canvas)
    bloodbox = Frame(6.9*inch, 4.5*inch, 1.2*inch, .3*inch, topPadding=0, bottomPadding=0, showBoundary=1)  
    bloodbox.addFromList([Paragraph(f"{employee_data['blood_group']}", sub_normal_style)], canvas)
    
    
    PHONEF = Frame(.7*inch, 4*inch, 1.5*inch, .4*inch,  topPadding=0, bottomPadding=0, showBoundary=0)
    PHONEF.addFromList([Paragraph("<b>PHONE:</b>", sub_normal_style)], canvas)
    PHONEBOX_1 = Frame(1.5*inch, 4.15*inch, 2.26*inch, .3*inch, topPadding=0, bottomPadding=0, showBoundary=1)  
    PHONEBOX_1.addFromList([Paragraph("", sub_normal_style)], canvas)
    
    i=0
    x=1.82
    while i<6:
      canvas.line(x*inch, 4.45*inch, x*inch, 4.15*inch)
      x += .32
      i += 1
    

    extF = Frame(6.32*inch,  4*inch, 1.7*inch, .4*inch,  topPadding=0, bottomPadding=0, showBoundary=0)
    extF.addFromList([Paragraph("<b>EXT:</b>", sub_normal_style)], canvas)
    extFbox = Frame(6.9*inch, 4.15*inch, .97*inch, .3*inch, topPadding=0, bottomPadding=0, showBoundary=1)  
    extFbox.addFromList([Paragraph("", sub_normal_style)], canvas)
    
    i=0
    x=7.22
    while i<2:
      canvas.line(x*inch, 4.45*inch, x*inch, 4.15*inch)
      x += .32
      i += 1
      
      
    PHONEF = Frame(.7*inch, 3.65*inch, 1.5*inch, .4*inch,  topPadding=0, bottomPadding=0, showBoundary=0)
    PHONEF.addFromList([Paragraph("<b>MOBILE NO:</b>", sub_normal_style)], canvas)
    PHONEBOX_1 = Frame(1.9*inch, 3.8*inch, 3.55*inch, .3*inch, topPadding=0, bottomPadding=0, showBoundary=1)  
    PHONEBOX_1.addFromList([Paragraph("", sub_normal_style)], canvas)
    
    i=0
    x=2.22
    while i<10:
      canvas.line(x*inch, 4.1*inch, x*inch, 3.80*inch)
      x += .32
      i += 1
      
      
    EMIALF = Frame(.7*inch, 3.3*inch, 1.5*inch, .4*inch,  topPadding=0, bottomPadding=0, showBoundary=0)
    EMIALF.addFromList([Paragraph("<b>EMIAL:</b>", sub_normal_style)], canvas)
    EMIALF_1 = Frame(1.5*inch, 3.45*inch, 5.81*inch, .3*inch, topPadding=0, bottomPadding=0, showBoundary=1)  
    EMIALF_1.addFromList([Paragraph("", sub_normal_style)], canvas)
    
    i=0
    x=1.82
    while i<17:
      canvas.line(x*inch, 3.75*inch, x*inch, 3.45*inch)
      x += .32
      i += 1

  
  
    DEPTF = Frame(.7*inch, 2.9*inch, 1.5*inch, .4*inch,  topPadding=0, bottomPadding=0, showBoundary=0)
    DEPTF.addFromList([Paragraph("<b>DEPARTMENT:</b>", sub_normal_style)], canvas)
    DEPTF_1 = Frame(2*inch, 3.05*inch, 2.97*inch, .3*inch, topPadding=0, bottomPadding=0, showBoundary=1)  
    DEPTF_1.addFromList([Paragraph(f"{employee_data['dept']}", sub_normal_style)], canvas)
    
    UNITF = Frame(5.3*inch, 2.9*inch, 1.5*inch, .4*inch,  topPadding=0, bottomPadding=0, showBoundary=0)
    UNITF.addFromList([Paragraph("<b>UNIT:</b>", sub_normal_style)], canvas)
    UNITF_1 = Frame(5.9*inch, 3.05*inch, 1.98*inch, .3*inch, topPadding=0, bottomPadding=0, showBoundary=1)  
    UNITF_1.addFromList([Paragraph(f" {employee_data['unit']}", sub_normal_style)], canvas)
    
    DESIGNF = Frame(.7*inch, 2.55*inch, 1.5*inch, .4*inch,  topPadding=0, bottomPadding=0, showBoundary=0)
    DESIGNF.addFromList([Paragraph("<b>DESIGNATION:</b>", sub_normal_style)], canvas)
    DESIGNF_1 = Frame(2*inch, 2.7*inch, 2.97*inch, .3*inch, topPadding=0, bottomPadding=0, showBoundary=1)  
    DESIGNF_1.addFromList([Paragraph(f"{employee_data['designation']}", sub_normal_style)], canvas)
    
    SIGNF = Frame(.7*inch, 2*inch, 1.5*inch, .4*inch,  topPadding=0, bottomPadding=0, showBoundary=0)
    SIGNF.addFromList([Paragraph("<b>SIGNATURE:</b>", sub_normal_style)], canvas)
    SIGNF_1 = Frame(2*inch, 2*inch, 2.97*inch, .6*inch, topPadding=0, bottomPadding=0, showBoundary=1)  
    SIGNF_1.addFromList([Paragraph("", sub_normal_style)], canvas)
    
    putsign_1 = Frame(2.5*inch, 1.7*inch, 2.97*inch, .3*inch, topPadding=0, bottomPadding=0, showBoundary=0)  
    putsign_1.addFromList([Paragraph("(Put your signature here)", sub_normal_style)], canvas)
    
    photo_1 = Frame(5.9*inch, 1.1*inch, 1.6*inch, 1.8*inch, topPadding=0, bottomPadding=0, showBoundary=1)  
    photo_1.addFromList([Paragraph("<br/>Passport size Color Photograph", normal_style)], canvas)
    
    
