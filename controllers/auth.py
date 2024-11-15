from sqlalchemy.orm import Session
from models import User, AuditLog
from schemas import UserCreate, Token
from utils import verify_password, get_password_hash, create_access_token
from fastapi import HTTPException, status
from datetime import timedelta
import os

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def create_new_user(db: Session, user: UserCreate):
    db_user = get_user(db, user.username)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    if user.role not in ["Read", "Read/Write"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role")
    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_password, role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    access_token = create_access_token(
        data={"sub": new_user.username, "role": new_user.role, "token_version": new_user.token_version}
    )
    return {"access_token": access_token, "token_type": "bearer"}

def login_user(db: Session, username: str, password: str):
    user = authenticate_user(db, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password"
        )
    user.token_version += 1  
    db.commit()
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.username,
            "role": user.role,
            "token_version": user.token_version
        },
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
