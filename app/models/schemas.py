from pydantic import BaseModel, EmailStr
from typing import Optional

#Patient model
class PatientData(BaseModel):
    Name: str
    PID: int
    Age: int
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

#Token model
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