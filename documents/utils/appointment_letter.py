from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Frame, PageBreak
from reportlab.lib.units import inch
from reportlab.lib import colors


def appointment_letter(appointment_info, pdf_file):
    
    flowables = []
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    normal_style.fontSize = 11
    normal_style.fontName = "Times-Roman"
    normal_style.leading = 15
    normal_style.alignment = 4
        
    flowables.append(Paragraph(f"""<br/>
                                <b>STRICTLY PRIVATE AND CONFIDENTIAL</b><br/>
                                {appointment_info['ref']}<br/>          
                                Date: {appointment_info['issue_date'].strftime("%d-%b-%Y")}<br/><br/>	    
                                <b>{appointment_info['name']}</b><br/>                                                                         		
                                Vill: {appointment_info['permanent_vill']} P.O: {appointment_info['permanent_PO']}<br/> 
                                P.S: {appointment_info['permanent_PS']} Dist: {appointment_info['permanent_dist']}<br/> <br/>
                                <b><u>Appointment - {appointment_info['designation']} for {appointment_info['unit']}</u></b><br/><br/>
                                <b>Dear Mr. {appointment_info['name']},</b><br/>
                                We are pleased to appoint you as <b>{appointment_info['designation']}</b> in <b>{appointment_info['unit']},</b>
                                T.K. Bhaban ({appointment_info['floor_location']} Floor), 13 Kawran Bazar, Dhaka -1215 under the following terms:

                               """,
                               style=normal_style))
    
    # Page Break to 2nd Page
    flowables.append(Spacer(1,15))
    flowables.append(PageBreak())
    flowables.append(Paragraph("",normal_style))
    # Page Break to 4th Page
    
    
    doc = SimpleDocTemplate(pdf_file, pagesize=letter, rightMargin=.5*inch)
    doc.build(flowables, onFirstPage=lambda canvas, doc: onfirstpage(canvas, doc, appointment_info), 
              onLaterPages=lambda canvas, doc: OnLaterPager(canvas, doc, appointment_info))

    
def onfirstpage(canvas, doc, appointment_info):
    style = getSampleStyleSheet()
    normal_style = style['Normal']
    normal_style.fontSize = 11
    normal_style.fontName = "Times-Roman"
    normal_style.leading = 15
    normal_style.alignment = 4
    
    
    sub_normal_style = ParagraphStyle(
        name= 'sub_normal_style',
        fontName = "Times-Italic",
        fontSize = 9,
        leading = 10,
    )
    
    # 1. Designation
    designation_point_frame = Frame(x1=1*inch, y1=6.3*inch, width=2*inch, height=.5*inch, showBoundary=0)
    designation_point_frame.addFromList([Paragraph("<b>1. &nbsp; &nbsp; &nbsp; Designation</b>", normal_style)], canv=canvas)
    designation_frame = Frame(x1=3.5*inch, y1=6.3*inch, width=4.5*inch, height=.5*inch, showBoundary=0)
    designation_frame.addFromList([Paragraph(f"<b>: {appointment_info['designation']}</b>", normal_style)], canv=canvas)
    
    # 2. Place of Posting
    place_of_posting_point_frame = Frame(x1=1*inch, y1=5.8*inch, width=2*inch, height=.5*inch, showBoundary=0)
    place_of_posting_point_frame.addFromList([Paragraph("<b>2. &nbsp; &nbsp; &nbsp; Place of Posting</b>", normal_style)], canv=canvas)
    place_of_posting_frame = Frame(x1=3.5*inch, y1=5.8*inch, width=4.5*inch, height=.5*inch, showBoundary=0)
    place_of_posting_frame.addFromList([Paragraph(f"<b>:</b> {appointment_info['location']}", normal_style)], canvas)
    place_of_posting_subtext_frame = Frame(x1=3.6*inch, y1=5.6*inch, width=4.45*inch, height=.5*inch, showBoundary=0)
    place_of_posting_subtext_frame.addFromList([Paragraph("You will have no objection to serve the company at \
                                                            any location within Bangladesh as and when required \
                                                            in the interest of the company", sub_normal_style)], canvas)
    
    # 3. Date of Joining
    DOJ_point_frame = Frame(x1=1*inch, y1=5.1*inch, width=2*inch, height=.5*inch, showBoundary=0)
    DOJ_point_frame.addFromList([Paragraph("<b>3. &nbsp; &nbsp; &nbsp;Date of Joining</b>", normal_style)], canvas)
    DOJ_frame = Frame(x1=3.5*inch, y1=5.1*inch, width=4.5*inch, height=.5*inch, showBoundary=0)
    DOJ_frame.addFromList([Paragraph(f": {appointment_info['DOJ'].strftime("%d-%b-%Y")}", normal_style)], canvas)
    
    # 4. Types of Service
    service_point_frame = Frame(x1=1*inch, y1=4.6*inch, width=2*inch, height=.5*inch, showBoundary=0)
    service_point_frame.addFromList([Paragraph("<b>4. &nbsp; &nbsp; &nbsp;Types of Service</b>", normal_style)], canvas)
    service_semicolon_frame = Frame(x1=3.5*inch, y1=4.1*inch, width=4.5*inch, height=1*inch, showBoundary=0)
    service_semicolon_frame.addFromList([Paragraph("<b>:</b>", normal_style)], canvas)
    service_frame = Frame(x1=3.6*inch, y1=4.1*inch, width=4.4*inch, height=1*inch, showBoundary=0)
    service_frame.addFromList([Paragraph("You are appointed with a probation period of 6 (six) months.\
                                            Depending on your performance, your appointment will be confirmed. \
                                            However, the management reserves the right to extend your probation \
                                            period, if deemed necessary.", normal_style)], canvas)
    
    # 5. Leave
    leave_point_frame = Frame(x1=1*inch, y1=3.4*inch, width=2*inch, height=.5*inch, showBoundary=0)
    leave_point_frame.addFromList([Paragraph("<b>5. &nbsp; &nbsp; &nbsp; Leave</b>", normal_style)], canvas)
    leave_semicolon_frame = Frame(x1=3.5*inch, y1=2.95*inch, width=4.5*inch, height=1*inch, showBoundary=0)
    leave_semicolon_frame.addFromList([Paragraph("<b>:</b>", normal_style)], canvas)
    leave_frame = Frame(x1=3.6*inch, y1=2.95*inch, width=4.4*inch, height=1*inch, showBoundary=0)
    leave_frame.addFromList([Paragraph("""During the probation period, only weekly holidays and Govt.
                                       holidays will be admissible. Due to extra work of the department,
                                       you may be requested to work on holidays.""", normal_style)], canvas)
    
    # 6. Salary
    salary_point_frame = Frame(x1=1*inch, y1=2.5*inch, width=2*inch, height=.5*inch, showBoundary=0)
    salary_point_frame.addFromList([Paragraph("<b>6. &nbsp; &nbsp; &nbsp; Salary</b>", normal_style)], canvas)
    salary_semicolon_frame = Frame(x1=3.5*inch, y1=2.05*inch, width=4.5*inch, height=1*inch, showBoundary=0)
    salary_semicolon_frame.addFromList([Paragraph("<b>:</b>", normal_style)], canvas)
    salary_frame = Frame(x1=3.6*inch, y1=2.05*inch, width=4.4*inch, height=1*inch, showBoundary=0)
    salary_frame.addFromList([Paragraph(f"""You will be paid a consolidated salary
                                        of <b> Tk. {appointment_info['salary']}.00</b> ({appointment_info['in_word']} Taka only) 
                                        per month. .""", normal_style)], canvas) # need to fix Salary as accounting format and in word format
    salary_sub_text = Frame(x1=3.6*inch, y1=1.6*inch, width=4.4*inch, height=1*inch, showBoundary=0)
    salary_sub_text.addFromList([Paragraph("Income tax will be borne by you.", sub_normal_style)], canvas)
    
    # 7. Responsibilities
    responsibilities_point_frame = Frame(x1=1*inch, y1=1.8*inch, width=2*inch, height=.5*inch, showBoundary=0)
    responsibilities_point_frame.addFromList([Paragraph("<b>7. &nbsp; &nbsp; &nbsp; Responsibilities</b>", normal_style)], canvas)
    responsibilities_frame = Frame(x1=3.5*inch, y1=1.8*inch, width=4.5*inch, height=.5*inch, showBoundary=0)
    responsibilities_frame.addFromList([Paragraph("<b>:</b> Job description is attached as Annexure – ‘A’", normal_style)], canvas)
    
    # 8. Service Rules & Regulation
    rules_point_frame = Frame(x1=1*inch, y1=1.2*inch, width=2.5*inch, height=.5*inch, showBoundary=0)
    rules_point_frame.addFromList([Paragraph("<b>8. &nbsp; &nbsp; &nbsp; Service Rules & Regulation</b>", normal_style)], canvas)
    rules_semicolon_frame = Frame(x1=3.5*inch, y1=.7*inch, width=4.5*inch, height=1*inch, showBoundary=0)
    rules_semicolon_frame.addFromList([Paragraph("<b>:</b>", normal_style)], canvas)
    rules_frame = Frame(x1=3.6*inch, y1=.7*inch, width=4.5*inch, height=1*inch, showBoundary=0)
    rules_frame.addFromList([Paragraph(f""" 
                                       You will be abide by the Rules, Regulations, 
                                       Customs and Practices of <b>{appointment_info['policy']}.</b> 
                                       You will report to <b>{appointment_info['report_to']}</b>.
                                       """, normal_style)], canvas)
    
def OnLaterPager(canvas, doc, appointment_info):
    
    style = getSampleStyleSheet()
    normal_style = style['Normal']
    normal_style.fontSize = 11
    normal_style.fontName = "Times-Roman"
    normal_style.leading = 13
    normal_style.alignment = 4
    
    sub_normal_style = ParagraphStyle(
        name= 'sub_normal_style',
        fontName = "Times-Italic",
        fontSize = 9,
        leading = 10,
    )

    # 9. Termination
    termination_point_frame = Frame(x1=1*inch, y1=9.3*inch, width=2*inch, height=.5*inch, showBoundary=0)
    termination_point_frame.addFromList([Paragraph("<b>9. &nbsp; &nbsp; &nbsp; Termination</b>", normal_style)], canv=canvas)
    termination_semicolon_frame = Frame(x1=3.5*inch, y1=8.8*inch, width=4.5*inch, height=1*inch, showBoundary=0)
    termination_semicolon_frame.addFromList([Paragraph("<b>:</b>", normal_style)], canvas)
    termination_frame = Frame(x1=3.6*inch, y1=8*inch, width=4.4*inch, height=1.8*inch, showBoundary=0)
    termination_frame.addFromList([Paragraph("""Your service is terminable at any point of time within
                                             probation period from either side without assigning 
                                             any reason whatsoever. In case of resignation, you have
                                             to give 1 (one) month’s prior written notice and shall 
                                             not leave the employment without properly handing over 
                                             the charges as well as a formal release order. Otherwise,
                                             company will not be liable to provide you any financial 
                                             benefits (including salary) and will deduct 1 (one) month’s
                                             salary from your final settlement.""", normal_style)], canvas)
    
    # 10. Exclusivity
    termination_point_frame = Frame(x1=1*inch, y1=7.2*inch, width=2*inch, height=.5*inch, showBoundary=0)
    termination_point_frame.addFromList([Paragraph("<b>10. &nbsp; &nbsp; &nbsp; Exclusivity</b>", normal_style)], canv=canvas)
    termination_semicolon_frame = Frame(x1=3.5*inch, y1=6.7*inch, width=4.5*inch, height=1*inch, showBoundary=0)
    termination_semicolon_frame.addFromList([Paragraph("<b>:</b>", normal_style)], canvas)
    termination_frame = Frame(x1=3.6*inch, y1=6.5*inch, width=4.4*inch, height=1.2*inch, showBoundary=0)
    termination_frame.addFromList([Paragraph("""During the service of this company, you shall not 
                                             be engaged in any other business or service of any 
                                             nature whatsoever. If you have found to be engaged 
                                             in any financial transaction with any competitor of 
                                             this company, the same shall be deemed as severe offence 
                                             and shall be treated accordingly""", normal_style)], canvas)
    
    # 11. Others  
    Others_point_frame = Frame(x1=1*inch, y1=6*inch, width=2*inch, height=.5*inch, showBoundary=0)
    Others_point_frame.addFromList([Paragraph("<b>11. &nbsp; &nbsp; &nbsp; Others</b>", normal_style)], canv=canvas)
    termination_semicolon_frame = Frame(x1=3.5*inch, y1=5.5*inch, width=4.5*inch, height=1*inch, showBoundary=0)
    termination_semicolon_frame.addFromList([Paragraph("<b>: </b>Submit a joining letter on the date of joining.", normal_style)], canvas)
    
    # Signatory
    signatory_frame = Frame(x1=1*inch, y1=3.8*inch, width=3*inch, height=1*inch, showBoundary=0)
    signatory_frame.addFromList([Paragraph("""
                                           <b>__________________________________<br/>
                                                Col Almas Raisul Ghani, psc, G (Retd)<br/>
                                                Director, HR & OD<br/>
                                                T.K. Group<br/>
                                            </b>
                                           """, normal_style)], canv=canvas)
    
    # CC
    CC_frame = Frame(x1=1*inch, y1=1.5*inch, width=3*inch, height=2*inch, showBoundary=0)
    CC4_CC5 = ""
    if appointment_info['CC4'] ==None and appointment_info['CC5'] == None:
        CC4_CC5 = f"""
                &nbsp; &nbsp; &nbsp;{appointment_info['CC6']} <br/>
                &nbsp; &nbsp; &nbsp;{appointment_info['CC7']} <br/>
        """
    elif appointment_info['CC4'] != None:
        CC4_CC5 = f"""
                &nbsp; &nbsp; &nbsp;{appointment_info['CC4']}<br/>
                &nbsp; &nbsp; &nbsp;{appointment_info['CC6']} <br/>
                &nbsp; &nbsp; &nbsp;{appointment_info['CC7']} <br/>
        """
    elif appointment_info['CC5'] != None:
        CC4_CC5 = f"""
                &nbsp; &nbsp; &nbsp;{appointment_info['CC5']}<br/>
                &nbsp; &nbsp; &nbsp;{appointment_info['CC6']} <br/>
                &nbsp; &nbsp; &nbsp;{appointment_info['CC7']} <br/>
        """
        
    CC_frame.addFromList([Paragraph(f"""
                                    Cc:<br/>												
                                        &nbsp; &nbsp; &nbsp;{appointment_info['CC1']}<br/>
                                        &nbsp; &nbsp; &nbsp;{appointment_info['CC2']}<br/>
                                        &nbsp; &nbsp; &nbsp;{appointment_info['CC3']}<br/>
                                        {CC4_CC5}

                                    """, normal_style)], canvas)
    
    canvas.showPage()
    
    flowables = []
    flowables.append(Paragraph(f"""
                                <b>STRICTLY PRIVATE AND CONFIDENTIAL</b><br/>
                               {appointment_info['ref']}<br/>        
                                Date: {appointment_info['issue_date'].strftime("%d-%b-%Y")}<br/><br/>	    
                                <b>{appointment_info['name']}</b><br/>                                                                         		
                                Vill: {appointment_info['permanent_vill']} P.O: {appointment_info['permanent_PO']}<br/> 
                                P.S: {appointment_info['permanent_PS']} Dist: {appointment_info['permanent_dist']}<br/> <br/>
                                <b><u>Appointment - {appointment_info['designation']} for {appointment_info['unit']}</u></b><br/><br/>
                                <b>Dear Mr. {appointment_info['name']},</b><br/>
                                We are pleased to appoint you as <b>{appointment_info['designation']}</b> in <b>{appointment_info['unit']},</b>
                                T.K. Bhaban ({appointment_info['floor_location']} Floor), 13 Kawran Bazar, Dhaka -1215 under the following terms:

                               """,
                               style=normal_style))
    
    # Page Break
    flowables.append(Spacer(1,15))
    
    # 3rd Page Frame
    front_text_frame = Frame(x1=1*inch, y1=6.8*inch, width=6.5*inch, height=2.8*inch, showBoundary=0)
    front_text_frame.addFromList(flowables, canv=canvas)
    
    # Director Signature
    director_signature = Frame(x1=4*inch, y1=8.7*inch, width=3.5*inch, height=.5*inch, showBoundary=0)
    director_signature.addFromList([Paragraph(f"{appointment_info['director_signature']} ..............................", normal_style)], canvas)

        
    # 1. Designation
    designation_point_frame = Frame(x1=1*inch, y1=6.3*inch, width=2*inch, height=.5*inch, showBoundary=0)
    designation_point_frame.addFromList([Paragraph("<b>1. &nbsp; &nbsp; &nbsp; Designation</b>", normal_style)], canv=canvas)
    designation_frame = Frame(x1=3.5*inch, y1=6.3*inch, width=4.5*inch, height=.5*inch, showBoundary=0)
    designation_frame.addFromList([Paragraph(f"<b>: {appointment_info['designation']}</b>", normal_style)], canv=canvas)
    
    # 2. Place of Posting
    place_of_posting_point_frame = Frame(x1=1*inch, y1=5.8*inch, width=2*inch, height=.5*inch, showBoundary=0)
    place_of_posting_point_frame.addFromList([Paragraph("<b>2. &nbsp; &nbsp; &nbsp; Place of Posting</b>", normal_style)], canv=canvas)
    place_of_posting_frame = Frame(x1=3.5*inch, y1=5.8*inch, width=4.5*inch, height=.5*inch, showBoundary=0)
    place_of_posting_frame.addFromList([Paragraph(f"<b>:</b> {appointment_info['location']}", normal_style)], canvas)
    place_of_posting_subtext_frame = Frame(x1=3.6*inch, y1=5.6*inch, width=4.45*inch, height=.5*inch, showBoundary=0)
    place_of_posting_subtext_frame.addFromList([Paragraph("You will have no objection to serve the company at \
                                                            any location within Bangladesh as and when required \
                                                            in the interest of the company", sub_normal_style)], canvas)
    
    # 3. Date of Joining
    DOJ_point_frame = Frame(x1=1*inch, y1=5.1*inch, width=2*inch, height=.5*inch, showBoundary=0)
    DOJ_point_frame.addFromList([Paragraph("<b>3. &nbsp; &nbsp; &nbsp;Date of Joining</b>", normal_style)], canvas)
    DOJ_frame = Frame(x1=3.5*inch, y1=5.1*inch, width=4.5*inch, height=.5*inch, showBoundary=0)
    DOJ_frame.addFromList([Paragraph(f": {appointment_info['DOJ'].strftime("%d-%b-%Y")}", normal_style)], canvas)
    
    # 4. Types of Service
    service_point_frame = Frame(x1=1*inch, y1=4.6*inch, width=2*inch, height=.5*inch, showBoundary=0)
    service_point_frame.addFromList([Paragraph("<b>4. &nbsp; &nbsp; &nbsp;Types of Service</b>", normal_style)], canvas)
    service_semicolon_frame = Frame(x1=3.5*inch, y1=4.1*inch, width=4.5*inch, height=1*inch, showBoundary=0)
    service_semicolon_frame.addFromList([Paragraph("<b>:</b>", normal_style)], canvas)
    service_frame = Frame(x1=3.6*inch, y1=4.1*inch, width=4.4*inch, height=1*inch, showBoundary=0)
    service_frame.addFromList([Paragraph("You are appointed with a probation period of 6 (six) months.\
                                            Depending on your performance, your appointment will be confirmed. \
                                            However, the management reserves the right to extend your probation \
                                            period, if deemed necessary.", normal_style)], canvas)
    
    # 5. Leave
    leave_point_frame = Frame(x1=1*inch, y1=3.4*inch, width=2*inch, height=.5*inch, showBoundary=0)
    leave_point_frame.addFromList([Paragraph("<b>5. &nbsp; &nbsp; &nbsp; Leave</b>", normal_style)], canvas)
    leave_semicolon_frame = Frame(x1=3.5*inch, y1=2.95*inch, width=4.5*inch, height=1*inch, showBoundary=0)
    leave_semicolon_frame.addFromList([Paragraph("<b>:</b>", normal_style)], canvas)
    leave_frame = Frame(x1=3.6*inch, y1=2.95*inch, width=4.4*inch, height=1*inch, showBoundary=0)
    leave_frame.addFromList([Paragraph("""During the probation period, only weekly holidays and Govt.
                                       holidays will be admissible. Due to extra work of the department,
                                       you may be requested to work on holidays.""", normal_style)], canvas)
    
    # 6. Salary
    salary_point_frame = Frame(x1=1*inch, y1=2.5*inch, width=2*inch, height=.5*inch, showBoundary=0)
    salary_point_frame.addFromList([Paragraph("<b>6. &nbsp; &nbsp; &nbsp; Salary</b>", normal_style)], canvas)
    salary_semicolon_frame = Frame(x1=3.5*inch, y1=2.05*inch, width=4.5*inch, height=1*inch, showBoundary=0)
    salary_semicolon_frame.addFromList([Paragraph("<b>:</b>", normal_style)], canvas)
    salary_frame = Frame(x1=3.6*inch, y1=2.05*inch, width=4.4*inch, height=1*inch, showBoundary=0)
    salary_frame.addFromList([Paragraph(f"""You will be paid a consolidated salary
                                        of <b> Tk. {appointment_info['salary']}.00 </b>({appointment_info['in_word']}  Taka only) 
                                        per month. .""", normal_style)], canvas) # need to fix Salary as accounting format and in word format
    salary_sub_text = Frame(x1=3.6*inch, y1=1.6*inch, width=4.4*inch, height=1*inch, showBoundary=0)
    salary_sub_text.addFromList([Paragraph("Income tax will be borne by you.", sub_normal_style)], canvas)
    
    # 7. Responsibilities
    responsibilities_point_frame = Frame(x1=1*inch, y1=1.8*inch, width=2*inch, height=.5*inch, showBoundary=0)
    responsibilities_point_frame.addFromList([Paragraph("<b>7. &nbsp; &nbsp; &nbsp; Responsibilities</b>", normal_style)], canvas)
    responsibilities_frame = Frame(x1=3.5*inch, y1=1.8*inch, width=4.5*inch, height=.5*inch, showBoundary=0)
    responsibilities_frame.addFromList([Paragraph("<b>:</b> Job description is attached as Annexure – ‘A’", normal_style)], canvas)
    
    # 8. Service Rules & Regulation
    rules_point_frame = Frame(x1=1*inch, y1=1.2*inch, width=2.5*inch, height=.5*inch, showBoundary=0)
    rules_point_frame.addFromList([Paragraph("<b>8. &nbsp; &nbsp; &nbsp; Service Rules & Regulation</b>", normal_style)], canvas)
    rules_semicolon_frame = Frame(x1=3.5*inch, y1=.7*inch, width=4.5*inch, height=1*inch, showBoundary=0)
    rules_semicolon_frame.addFromList([Paragraph("<b>:</b>", normal_style)], canvas)
    rules_frame = Frame(x1=3.6*inch, y1=.7*inch, width=4.5*inch, height=1*inch, showBoundary=0)
    rules_frame.addFromList([Paragraph(f""" 
                                       You will be abide by the Rules, Regulations, 
                                       Customs and Practices of <b>{appointment_info['policy']}.</b> 
                                       You will report to <b>{appointment_info['report_to']}</b>.
                                       """, normal_style)], canvas)
    
    
    # 4th Page
    canvas.showPage()
    
    # 9. Termination
    termination_point_frame = Frame(x1=1*inch, y1=9.3*inch, width=2*inch, height=.5*inch, showBoundary=0)
    termination_point_frame.addFromList([Paragraph("<b>9. &nbsp; &nbsp; &nbsp; Termination</b>", normal_style)], canv=canvas)
    termination_semicolon_frame = Frame(x1=3.5*inch, y1=8.8*inch, width=4.5*inch, height=1*inch, showBoundary=0)
    termination_semicolon_frame.addFromList([Paragraph("<b>:</b>", normal_style)], canvas)
    termination_frame = Frame(x1=3.6*inch, y1=8*inch, width=4.4*inch, height=1.8*inch, showBoundary=0)
    termination_frame.addFromList([Paragraph("""Your service is terminable at any point of time within
                                             probation period from either side without assigning 
                                             any reason whatsoever. In case of resignation, you have
                                             to give 1 (one) month’s prior written notice and shall 
                                             not leave the employment without properly handing over 
                                             the charges as well as a formal release order. Otherwise,
                                             company will not be liable to provide you any financial 
                                             benefits (including salary) and will deduct 1 (one) month’s
                                             salary from your final settlement.""", normal_style)], canvas)
    
    # 10. Exclusivity
    termination_point_frame = Frame(x1=1*inch, y1=7.2*inch, width=2*inch, height=.5*inch, showBoundary=0)
    termination_point_frame.addFromList([Paragraph("<b>10. &nbsp; &nbsp; &nbsp; Exclusivity</b>", normal_style)], canv=canvas)
    termination_semicolon_frame = Frame(x1=3.5*inch, y1=6.7*inch, width=4.5*inch, height=1*inch, showBoundary=0)
    termination_semicolon_frame.addFromList([Paragraph("<b>:</b>", normal_style)], canvas)
    termination_frame = Frame(x1=3.6*inch, y1=6.5*inch, width=4.4*inch, height=1.2*inch, showBoundary=0)
    termination_frame.addFromList([Paragraph("""During the service of this company, you shall not 
                                             be engaged in any other business or service of any 
                                             nature whatsoever. If you have found to be engaged 
                                             in any financial transaction with any competitor of 
                                             this company, the same shall be deemed as severe offence 
                                             and shall be treated accordingly""", normal_style)], canvas)
    
    # 11. Others  
    Others_point_frame = Frame(x1=1*inch, y1=6*inch, width=2*inch, height=.5*inch, showBoundary=0)
    Others_point_frame.addFromList([Paragraph("<b>11. &nbsp; &nbsp; &nbsp; Others</b>", normal_style)], canv=canvas)
    termination_semicolon_frame = Frame(x1=3.5*inch, y1=5.5*inch, width=4.5*inch, height=1*inch, showBoundary=0)
    termination_semicolon_frame.addFromList([Paragraph("<b>: </b>Submit a joining letter on the date of joining.", normal_style)], canvas)
    
    # Signatory
    signatory_frame = Frame(x1=1*inch, y1=3.8*inch, width=3*inch, height=1*inch, showBoundary=0)
    signatory_frame.addFromList([Paragraph("""
                                           <b>__________________________________<br/>
                                                Col Almas Raisul Ghani, psc, G (Retd)<br/>
                                                Director, HR & OD<br/>
                                                T.K. Group<br/>
                                            </b>
                                           """, normal_style)], canv=canvas)
    # Receiving Signature
    receiving_signature = Frame(x1=5*inch, y1=3*inch, width=2*inch, height=1.5*inch, showBoundary=0)
    receiving_signature.addFromList([Paragraph(""" 
                                                 &nbsp; &nbsp; &nbsp; &nbsp; Received by:<br/><br/><br/>
                                                ………………………….<br/>
                                                 &nbsp; &nbsp; &nbsp; Name & Signature 
                                                
                                                """, normal_style)], canvas)
    
    
    
    
    
    # CC
    CC_frame = Frame(x1=1*inch, y1=1.5*inch, width=3*inch, height=2*inch, showBoundary=0)
    CC4_CC5 = ""
    if appointment_info['CC4'] !=None and appointment_info['CC5'] != None:
        CC4_CC5 = f"""
                &nbsp; &nbsp; &nbsp;{appointment_info['CC4']}<br/>
                &nbsp; &nbsp; &nbsp;{appointment_info['CC5']}<br/>
                &nbsp; &nbsp; &nbsp;{appointment_info['CC6']} <br/>
                &nbsp; &nbsp; &nbsp;{appointment_info['CC7']} <br/>
        """
    elif appointment_info['CC4'] != None:
        CC4_CC5 = f"""
                &nbsp; &nbsp; &nbsp;{appointment_info['CC4']}<br/>
                &nbsp; &nbsp; &nbsp;{appointment_info['CC6']} <br/>
                &nbsp; &nbsp; &nbsp;{appointment_info['CC7']} <br/>
        """
    elif appointment_info['CC5'] != None:
        CC4_CC5 = f"""
                &nbsp; &nbsp; &nbsp;{appointment_info['CC5']}<br/>
                &nbsp; &nbsp; &nbsp;{appointment_info['CC6']} <br/>
                &nbsp; &nbsp; &nbsp;{appointment_info['CC7']} <br/>
        """
    else:
        CC4_CC5 = f"""

            &nbsp; &nbsp; &nbsp;{appointment_info['CC6']} <br/>
            &nbsp; &nbsp; &nbsp;{appointment_info['CC7']} <br/>
        """
          
    CC_frame.addFromList([Paragraph(f"""
                                    Cc:<br/>												
                                        &nbsp; &nbsp; &nbsp;{appointment_info['CC1']}<br/>
                                        &nbsp; &nbsp; &nbsp;{appointment_info['CC2']}<br/>
                                        &nbsp; &nbsp; &nbsp;{appointment_info['CC3']}<br/>
                                        {CC4_CC5}

                                    """, normal_style)], canvas)
    