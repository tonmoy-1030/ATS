from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime


def InterviewSummary(file_path, interview_summary):
    # Create the PDF
    doc = SimpleDocTemplate(
        file_path,
        pagesize=landscape(A4),
        rightMargin=40,
        leftMargin=40,
        topMargin=50,
        bottomMargin=20,
        title="Interview Summary"
    )

    # Styles
    styles = getSampleStyleSheet()
    label_style = ParagraphStyle(
        "LabelStyle",
        parent=styles["Normal"],
        fontName="Times-Bold",
        fontSize=14,
        leftIndent=20,
        leading=20
    )
    
    list_style = ParagraphStyle(
        "LabelStyle",
        parent=styles["Normal"],
        fontName="Times-Bold",
        fontSize=14,
        leftIndent=50,
        leading=20
    )

    # Flowables list 
    elements = []

    # Main data table
    data_labels = [
        ("Date", "date"),
        ("Unit", "unit"),
        ("Position", "position"),
        (
            "Total Applicants Called for Preliminary Interview",
            "total_applicant_in_initial_interview",
        ),
        (
            "Total Applicants Absent in Preliminary Interview",
            "total_applicant_absent_in_initial_interview",
        ),
        (
            "Total Applicants Interviewed in Preliminary Interview",
            "total_applicant_interviewed_in_initial_interview",
        ),
        (
            "Total Applicants Shortlisted for Final Interview",
            "total_applicant_shortlisted_in_final_interview",
        ),
        (
            "Total Applicants Present in Final Interview",
            "total_applicant_present_in_final_interview",
        ),
        (
            "Total Applicants Absent in Final Interview",
            "total_applicant_absent_in_final_interview",
        ),
        ("Total Number of Vacancy", "total_vacancy"),
    ]

    table_data = []
    for label, key in data_labels:
        table_data.append([label, interview_summary[key]])

    main_table = Table(table_data, colWidths=[500, 200])
    main_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Times-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 14),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("ALIGN", (-1, 0), (-1, -1), "CENTER"),
            ]
        )
    )
    elements.append(main_table)
    elements.append(Spacer(20,20))
    elements.append(Paragraph("Interviewed by:", label_style))
    elements.append(Spacer(20,20))
    interviewed_by_text = f"{interview_summary['interviewed_by'].replace('\n', '<br/>')}"
    elements.append(Paragraph(interviewed_by_text, list_style))
    
    # Build PDF
    doc.build(elements)

