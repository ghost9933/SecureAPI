from passlib.context import CryptContext  # Install passlib
from datetime import datetime, timedelta
import jwt  
import os
from dotenv import load_dotenv  
from typing import Optional

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "9BFB57556573D6CDCBCE8AE6835DA")  
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()

    token_version = to_encode.get("token_version", 0)
    to_encode.update({"token_version": token_version})   
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
