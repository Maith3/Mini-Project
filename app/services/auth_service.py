from app.models.schemas import UserInDB
from app.core.security import verify_password
from fastapi import HTTPException, Depends, status
from app.core.security import oauth_2_scheme
from jose import jwt, JWTError
from app.core.config import SECRET_KEY, ALGORITHM
from app.core.database import users_collection
from app.models.schemas import TokenData

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