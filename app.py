from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
import pandas as pd
import joblib
import shap
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from reportlab.lib import colors


#Loading saved model
model = joblib.load('Fmodel.joblib')

explainer = shap.TreeExplainer(model)

#Creating a reference to a fastapi object
app = FastAPI()

#Input Schema
class PatientData(BaseModel):
    Name: str
    PID: int
    BMI: float
    Systolic_BP: float
    Diabetes_Status: int
    Estimated_LDL: float
    Total_Cholesterol: float
    HDL: float

#Home route
@app.get("/")
def home():
    return {"message":"CVD Risk Prediction API Running"}

#Prediction route
@app.post("/predict")
def predict(data: PatientData):
    #Converting input to dataframe
    input_data = pd.DataFrame([{
        "BMI": data.BMI,
        "Total Cholesterol (mg/dL)": data.Total_Cholesterol,
        "HDL (mg/dL)": data.HDL,
        "Diabetes Status": data.Diabetes_Status,
        "Systolic BP": data.Systolic_BP,
        "Estimated LDL (mg/dL)": data.Estimated_LDL
    }])
    
    #Predict risk
    prediction = model.predict(input_data)[0]
    
    if prediction < 14:
        risk_category = "Low Risk"
    elif prediction < 18:
        risk_category = "Moderate Risk"
    else:
        risk_category = "High Risk"
    
    shap_values = explainer(input_data)
    feature_importance={}
    for feature, value in zip(input_data.columns, shap_values.values[0]):
        feature_importance[feature] = round(float(value),3)
    
    #Sort by absolute contribution
    sorted_features = dict(
        sorted(
            feature_importance.items(),
            key = lambda item: abs(item[1]),
            reverse = True
        )
    )
    return generatePdf(risk_category,data,prediction,sorted_features)
    """#Return response
    return{"Predicted CVD Risk Score": round(float(prediction),2),
        "Risk Category": risk_category,
        "Top Contributing Factors": sorted_features}"""
    
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
            f"Patient ID: {data.PID}",
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
    
def get_parameter_table(data):
    table = [['Parameter','Patient Value', 'Normal Range', 'Status']]
    status={}
    
    #BMI
    if data.BMI < 18.5:
        status['BMI'] = 'Underweight'
    elif data.BMI < 25:
        status['BMI'] = 'Normal'
    elif data.BMI <30:
        status['BMI'] = 'Overweight'
    elif data.BMI>30:
        status['BMI'] = 'Obese'
        
    #Systolic BP
    if data.Systolic_BP<90:
        status['Systolic_BP'] = 'Low'
    elif data.Systolic_BP<=120:
        status['Systolic_BP'] = 'Normal'
    elif data.Systolic_BP<=139:
        status['Systolic_BP'] = 'Elevated'
    elif data.Systolic_BP>=140:
        status['Systolic_BP'] = 'High'
        
    #Diabetes Status
    if data.Diabetes_Status == 0:
        status['Diabetes_Status'] = 'Non-Diabetic'
    elif data.Diabetes_Status == 1:
        status['Diabetes_Status'] = 'Diabetic'
        
    #Estimated LDL
    if data.Estimated_LDL < 100:
        status['Estimated_LDL'] = 'Optimal'
    elif data.Estimated_LDL < 130:
        status['Estimated_LDL'] = 'Near Optimal'
    elif data.Estimated_LDL < 160:
        status['Estimated_LDL'] = 'Borderline High'
    elif data.Estimated_LDL < 190:
        status['Estimated_LDL'] = 'High'
    elif data.Estimated_LDL > 190:
        status['Estimated_LDL'] = 'Very High'
    
    #Total Cholesterol
    if data.Total_Cholesterol < 200:
        status['Total_Cholesterol'] = 'Desirable'
    elif data.Total_Cholesterol < 240:
        status['Total_Cholesterol'] = 'BorderLine High'
    elif data.Total_Cholesterol >= 240:
        status['Total_Cholesterol'] = 'High'
    
    #HDL
    if data.HDL < 40:
        status['HDL'] = 'Low'
    elif data.HDL < 60:
        status['HDL'] = 'Normal'
    elif int(data.HDL) in range(60,90):
        status['HDL'] = 'Protective'
    elif data.HDL >= 90:
        status['HDL'] = 'High'
    
    table.append([
        'BMI',
        data.BMI,
        '18.5 - 24.9',
        status['BMI']
    ])
    
    table.append([
        'Systolic BP',
        data.Systolic_BP,
        '90 - 120 mmHg',
        status['Systolic_BP']
    ])
    
    table.append([
        'Diabetes Status',
        data.Diabetes_Status,
        '0 = Non-Diabetic',
        status['Diabetes_Status']
    ])
    
    table.append([
        'Estimated LDL',
        data.Estimated_LDL,
        '< 100 mg/dL',
        status['Estimated_LDL']
    ])
    
    table.append([
        'Total Cholesterol',
        data.Total_Cholesterol,
        '< 200 mg/dL',
        status['Total_Cholesterol']
    ])
    
    table.append([
        'HDL',
        data.HDL,
        '> 60 mg/dL',
        status['HDL']
    ])
    
    return table