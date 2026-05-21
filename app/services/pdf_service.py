from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from fastapi.responses import StreamingResponse
from app.utils.health_utils import get_parameter_table

def generatePdf(risk_category, data, prediction, sorted_features):
    #pdf = SimpleDocTemplate("report.pdf")
    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer)
    
    styles = getSampleStyleSheet()
    elements=[]
    styles['Heading1'].fontSize = 16
    styles['Title'].fontSize = 18
    styles['BodyText'].fontSize = 12
    styles['Heading2'].fontSize=14
    
    text = Paragraph('CVD Risk Report', styles['Title'])
    elements.append(text)
    text = Paragraph(f"<br/><br/><br/>Patient Name: {data.Name}<br/>"
            f"Patient ID: {data.PID}<br/>"
            f"Patient Age: {data.Age}<br/>",
            styles['Heading2']
            )
    """return FileResponse(
        path = "report.pdf",
        filename="CVD_Rep.pdf",
        media_type='application/pdf'
    )""" #However on download local storage is being used
    elements.append(text)
    elements.append(Spacer(1,20))
    text = Paragraph(f"<b>CVD Risk Score:</b> {round(float(prediction),2)}<br/><br/>"
                    f"<b>Risk Level:</b> {risk_category}",
                    styles['BodyText'])
    elements.append(text)
    elements.append(Spacer(1,20))
    text = Paragraph('Parameter Table', styles['Heading2'])
    elements.append(text)
    table_data=get_parameter_table(data)
    parameter_table = Table(table_data, hAlign='LEFT')
    parameter_table.setStyle(TableStyle([
    # Header Background
    ('BACKGROUND', (0,0), (-1,0), colors.grey),

    # Header Text Color
    ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),

    # Header Font
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),

    # Header Font Size
    ('FONTSIZE', (0,0), (-1,0), 12),

    # Body Font Size
    ('FONTSIZE', (0,1), (-1,-1), 11),

    # Alignment
    ('ALIGN', (0,0), (-1,-1), 'CENTER'),

    # Grid Lines
    ('GRID', (0,0), (-1,-1), 1, colors.black),

    # Padding
    ('BOTTOMPADDING', (0,0), (-1,0), 12),

    # Background for Body
    ('BACKGROUND', (0,1), (-1,-1), colors.beige)]))
    elements.append(Spacer(1,10))
    elements.append(parameter_table)
    elements.append(Spacer(1,20))
    #Adding Top Features
    text = Paragraph(
        "Feature Contribution Analysis",
        styles['Heading2']
    )
    elements.append(Spacer(1,10))
    elements.append(text)
    feature_text = ""

    for feature, value in sorted_features.items():

        feature_text += (
            f"{feature} : {value}<br/><br/>")
    text = Paragraph(
    feature_text,
    styles['BodyText'])
    elements.append(text)
    elements.append(Spacer(1,5))
    text = Paragraph(f"<i>Negative value results in <b>decrease</b> of CVD Risk<br/>Positive value results in <b>increase</b> of CVD Risk</i>",styles['BodyText'])
    elements.append(text)
    #Building the pdf
    pdf.build(elements)
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers = {"Content-Disposition":"attachment; filename=CVD_Report.pdf"}
        )
    
