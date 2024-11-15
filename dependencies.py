from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import jwt
from jwt import PyJWTError
from typing import Generator
from models import User
from database import SessionLocal
from schemas import TokenData
from controllers.auth import get_user
from utils import SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,  
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        token_version: int = payload.get("token_version", 0)  
        if username is None or role is None:
            raise credentials_exception
        token_data = TokenData(username=username, role=role, token_version=token_version)
    except PyJWTError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None or user.token_version != token_data.token_version:
        raise credentials_exception
    return user

async def read_permission(current_user: User = Depends(get_current_user)):
    if current_user.role not in ["Read", "Read/Write"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Operation not permitted")
    return current_user

async def write_permission(current_user: User = Depends(get_current_user)):
    if current_user.role != "Read/Write":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Operation not permitted")
    return current_user
