from app.models.schemas import UserSignup, Token
from app.core.database import users_collection
from fastapi import HTTPException, status, Depends
from app.core.security import get_password_hash, create_access_token
from dotenv import load_dotenv
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from app.services.auth_service import authenticate_user
from fastapi import APIRouter
from app.models.schemas import (
    ForgotPasswordRequest,
    ResetPasswordRequest
)

from app.services.auth_service import (
    forgot_password_service,
    reset_password_service
)

router = APIRouter()

@router.post("/signup")
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

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Incorrect username or password",
                            headers={"WWW-Authenticate":"Bearer"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub":user.username}, expires_delta=access_token_expires)
    return {"access_token":access_token,"token_type":"bearer"}

@router.post("/forgot-password")
async def forgot_password(data: ForgotPasswordRequest):

    return await forgot_password_service(data.email)


@router.post("/reset-password")
async def reset_password(data: ResetPasswordRequest):

    return await reset_password_service(
        data.email,
        data.otp,
        data.new_password
    )

