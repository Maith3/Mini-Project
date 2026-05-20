import pandas as pd
from app.models.schemas import PatientData, User
from fastapi import Depends
from app.services.auth_service import get_current_active_user
from fastapi import APIRouter
from app.services.pdf_service import generatePdf
from app.services.prediction_service import predict_risk

router = APIRouter()

@router.get("/")
def home():
    return {"message":"CVD Risk Prediction API Running"}

#Prediction route
@router.post("/predict")
async def predict(data: PatientData, current_user: User=Depends(get_current_active_user)):
    #Converting input to dataframe
    prediction, risk_category, sorted_features = await predict_risk(data)

    return generatePdf(
        risk_category,
        data,
        prediction,
        sorted_features
    )