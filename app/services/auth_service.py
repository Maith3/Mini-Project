from app.models.schemas import UserInDB
from app.core.security import verify_password
from fastapi import HTTPException, Depends, status
from app.core.security import oauth_2_scheme
from jose import jwt, JWTError
from app.core.config import SECRET_KEY, ALGORITHM
from app.core.database import users_collection
from app.models.schemas import TokenData
from app.core.security import (
    create_reset_token,
    verify_reset_token,
    get_password_hash
)
from app.utils.email_utils import send_reset_email, send_otp_email
import random
from datetime import timedelta, datetime

def get_user(username: str):
    user_data = users_collection.find_one({"username": username})
    
    if user_data:
        return UserInDB(**user_data)
    
    return None

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

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
    user = get_user(username=token_data.username)
    if user is None:
        raise credential_exception
    return user

async def get_current_active_user(current_user:UserInDB = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive User")
    if not current_user.verified:
        raise HTTPException(status_code=403, detail="User not verified yet")
    return current_user

async def forgot_password_service(email: str):

    user = users_collection.find_one({"email": email})

    if not user:
        return {
            "message": "If email exists, OTP sent"
        }

    otp = str(random.randint(100000, 999999))

    expiry = datetime.utcnow() + timedelta(minutes=5)

    users_collection.update_one(
        {"email": email},
        {
            "$set": {
                "otp": otp,
                "otp_expiry": expiry
            }
        }
    )

    await send_otp_email(email, otp)

    return{"OTP sent successfully"}


# ======================================
# RESET PASSWORD SERVICE
# ======================================


async def reset_password_service(
    email: str,
    otp: str,
    new_password: str
):

    user = users_collection.find_one({"email": email})

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user.get("otp") != otp:
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP"
        )

    if datetime.utcnow() > user.get("otp_expiry"):
        raise HTTPException(
            status_code=400,
            detail="OTP expired"
        )

    hashed_password = get_password_hash(new_password)

    users_collection.update_one(
        {"email": email},
        {
            "$set": {
                "hashed_password": hashed_password
            },
            "$unset": {
                "otp": "",
                "otp_expiry": ""
            }
        }
    )

    return {
        "message": "Password reset successful"
    }