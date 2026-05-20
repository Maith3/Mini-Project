from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, EmailStr
import pandas as pd
import joblib
import shap
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from reportlab.lib import colors
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
import os
from pymongo import MongoClient
from typing import Optional

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
MONGO_URL = os.getenv("MONGO_URL")

client = MongoClient(MONGO_URL)
try: 
    client.admin.command('ping')
    print('MongoDB Connected Successfully!')
except Exception as e:
    print(e)

db = client["cvd_database"]
users_collection = db['users']
reports_collection = db['reports']

#Loading saved model
model = joblib.load('Fmodel.joblib')

explainer = shap.TreeExplainer(model)

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

#Signup model
class UserSignup(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str
    hospitalName: str
    HP_ID: str 

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None 

class User(BaseModel):
    username: str
    email: EmailStr
    disabled: bool = False
    verified: bool = False
    
class UserInDB(User):
    hashed_password: str

pwd_context = CryptContext(schemes=['bcrypt'],deprecated='auto')
oauth_2_scheme = OAuth2PasswordBearer(tokenUrl="token")

#Creating a reference to a fastapi object
app = FastAPI()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password,hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(users_collection, username: str):
    user_data = users_collection.find_one({"username": username})
    
    if user_data:
        return UserInDB(**user_data)
    
    return None

def authenticate_user(users_collection, username: str, password: str):
    user = get_user(users_collection,username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data:dict, expires_delta: Optional[timedelta]=None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp":expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth_2_scheme)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials",
                                        headers={"WWW-Authenticate":"Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credential_exception
        token_data = TokenData(username=username)  
    except JWTError:
        raise credential_exception
    user = get_user(users_collection, username=token_data.username)
    if user is None:
        raise credential_exception
    return user

async def get_current_active_user(current_user:UserInDB = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive User")
    if not current_user.verified:
        raise HTTPException(status_code=403, detail="User not verified yet")
    return current_user
        

@app.post("/signup")
async def signup(user:UserSignup):
    existing_user = users_collection.find_one(
        {"username": user.username}
    )
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )
    existing_email = users_collection.find_one(
        {"email": user.email}
    )
    
    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    hashed_password = get_password_hash(user.password)
    
    user_data = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_password,
        "role": user.role,
        "hospitalName": user.hospitalName,
        "HP_ID": user.HP_ID,
        "disabled": False,
        "verified": False
    }
    users_collection.insert_one(user_data)
    return {"message": "User created successfully"
    }
    
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(users_collection, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Incorrect username or password",
                            headers={"WWW-Authenticate":"Bearer"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub":user.username}, expires_delta=access_token_expires)
    return {"access_token":access_token,"token_type":"bearer"}

#Home route
@app.get("/")
def home():
    return {"message":"CVD Risk Prediction API Running"}

#Prediction route
@app.post("/predict")
async def predict(data: PatientData, current_user: User=Depends(get_current_active_user)):
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
    elif data.BMI>=30:
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
    elif data.Estimated_LDL >= 190:
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