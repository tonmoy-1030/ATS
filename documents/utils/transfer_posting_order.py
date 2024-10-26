from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.lib import colors
from dateutil.relativedelta import relativedelta



def transfer_letter(transfer_data, pdf_file):
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
    
    title_style = ParagraphStyle(
        name='TitleStyle',
        fontName="Times-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.black,
        alignment=1,  # Center alignment
    )

    normal_styles = styles['Normal']
    normal_styles.fontName = "Times-Roman"
    normal_styles.fontSize = 11
    normal_styles.alignment = 4
    # Add header paragraph
    header = f"""
    <br/><br/><br/><br/>
    {transfer_data['ref']}<br/>
    {transfer_data['issue_date'].strftime("%d-%b-%Y")}<br/><br/>								           

    <b>{transfer_data['name']}</b><br/>
    <b>Employee ID: {transfer_data['EID']}</b><br/>
   {transfer_data['designation']}<br/>
    {transfer_data['current_location']} <br/>
    {transfer_data['unit']}<br/><br/><br/>

    """
    flowables.append(Paragraph(header, normal_styles))
    flowables.append(Spacer(1, 15))
    
    title_text = "<b><u>Transfer Order</u></b><br/>"
    
    flowables.append(Paragraph(title_text, title_style))
    flowables.append(Spacer(1, 15))
    
    if transfer_data['current_region/zone'] != None:
        current_region ="under " + transfer_data['current_region/zone']
        current_region_type = transfer_data['current_region/zone_type']
    else:
        current_region = ""
        current_region_type = ""
    
    if transfer_data['new_region/zone'] != None:
        new_region =  "under " + transfer_data['new_region/zone']
        new_region_type = transfer_data['new_region/zone_type']
    else:
        new_region = ""
        new_region_type =""
    
    body_text = f"""
    Dear Mr. {transfer_data['name']},<br/><br/>
    This is to inform you that the Management of T.K. Group has decided to transfer you from
    {transfer_data["current_location"]} {transfer_data['current_type']} {current_region} {current_region_type} 
    to {transfer_data['new_location']} {transfer_data['new_type']} {new_region} {new_region_type} 
    as {transfer_data['new_designation']} with effect from {transfer_data['effective_date'].strftime("%d-%b-%Y")}.
    """
    flowables.append(Paragraph(body_text, body_style))
    flowables.append(Spacer(1, 15))
    

        
    body_text_2 =f"""
    
    You will report to <b>{transfer_data['report_to']}</b><br/><br/>
    Your, salary, benefit and all other terms and conditions of employment will remain the same.<br/><br/>
    We firmly believe that you will carry out your duties and responsibilities diligently and 
    accomplish your future assignments efficiently and effectively.<br/><br/><br/>
    
    """
    flowables.append(Paragraph(body_text_2, body_style))
    flowables.append(Spacer(1, 15))
        
    
    
    signature_text = f"""
        <b>_________________________</b><br/> 				
        <b>{transfer_data["signature"]}</b><br/> 						                             
        <b>{transfer_data["signature_designation"]}</b><br/> 
        <b>T.K. Group</b><br/> <br/> <br/> <br/> 

        Cc:<br/> 								
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{transfer_data["business_director"]}<br/>  
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Head of Business<br/> 
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Accounts Department<br/>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Personal files<br/> 
    """
    flowables.append(Paragraph(signature_text, normal_styles))
    flowables.append(Spacer(1, 15))
    doc = SimpleDocTemplate(pdf_file, pagesize=letter, bottomMargin=0*inch)
    doc.build(flowables)


def posting_letter(transfer_data, pdf_file):
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
    
    title_style = ParagraphStyle(
        name='TitleStyle',
        fontName="Times-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.black,
        alignment=1,  # Center alignment
    )

    normal_styles = styles['Normal']
    normal_styles.fontName = "Times-Roman"
    normal_styles.fontSize = 11
    normal_styles.alignment = 4
    # Add header paragraph
    header = f"""
    <br/><br/><br/><br/>
    {transfer_data['ref']}<br/>
    {transfer_data['issue_date'].strftime("%d-%b-%Y")}<br/><br/>								           

    <b>{transfer_data['name']}</b><br/>
    <b>Employee ID: {transfer_data['EID']}</b><br/>
   {transfer_data['designation']}<br/>
    {transfer_data['unit']} <br/><br/><br/>

    """
    flowables.append(Paragraph(header, normal_styles))
    flowables.append(Spacer(1, 15))
    
    title_text = "<b><u>Posting Order</u></b><br/>"
    
    flowables.append(Paragraph(title_text, title_style))
    flowables.append(Spacer(1, 15))

    if transfer_data['new_region/zone'] != None:
        new_region =  "under " + transfer_data['new_region/zone']
        new_type = transfer_data['new_region/zone_type']
    else:
        new_region = ""
        new_type = ""
    
    body_text = f"""
    Dear Mr. {transfer_data['name']},<br/><br/>
    
    This is to inform you that the Management of T.K. Group has decided your work location
    at {transfer_data['new_location']} {transfer_data['new_type']} {new_region} {new_type} with effect from {transfer_data['effective_date'].strftime("%d-%b-%Y")}.
    """
    flowables.append(Paragraph(body_text, body_style))
    flowables.append(Spacer(1, 15))
    

        
    body_text_2 =f"""
    
    You will report to <b>{transfer_data['report_to']}</b><br/><br/>
    Your, salary, benefit and all other terms and conditions of employment will remain the same.<br/><br/>
    We firmly believe that you will carry out your duties and responsibilities diligently and 
    accomplish your future assignments efficiently and effectively.<br/><br/><br/>
    
    """
    flowables.append(Paragraph(body_text_2, body_style))
    flowables.append(Spacer(1, 15))
        
    
    
    signature_text = f"""
        <b>________________________</b><br/> 				
        <b>{transfer_data["signature"]}</b><br/> 						                             
        <b>{transfer_data["signature_designation"]}</b><br/> 
        <b>T.K. Group</b><br/> <br/> <br/> <br/> 

        Cc:<br/> 								
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;>{transfer_data["business_director"]}<br/>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Head of Business<br/> 
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Accounts Department<br/>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Personal files<br/> 
    """
    flowables.append(Paragraph(signature_text, normal_styles))
    flowables.append(Spacer(1, 15))
    doc = SimpleDocTemplate(pdf_file, pagesize=letter, bottomMargin=0*inch)
    doc.build(flowables)
