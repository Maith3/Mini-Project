from app.models.schemas import PatientData
import pandas as pd
from app.ml.model_loader import model
from app.ml.shap_explainer import explainer

async def predict_risk(data: PatientData):
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
    return prediction, risk_category, sorted_features