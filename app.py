from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import joblib
import shap

#Loading saved model
model = joblib.load('Fmodel.joblib')

explainer = shap.TreeExplainer(model)

#Creating a reference to a fastapi object
app = FastAPI()

#Input Schema
class PatientData(BaseModel):
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
    #Return response
    return{"Predicted CVD Risk Score": round(float(prediction),2),
        "Risk Category": risk_category,
        "Top Contributing Factors": sorted_features}
    
    