# app.py

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validator
from typing import List, Optional, Generator
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta
import re
import os
import jwt  # Install PyJWT
from passlib.context import CryptContext  # Install passlib
from dotenv import load_dotenv  # Install python-dotenv

# Load environment variables from a .env file
load_dotenv()

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")  # Replace with your own secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/phonebook.db")  # Use relative 'data/' directory

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)
Base = declarative_base()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Models
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String)  # 'Read' or 'Read/Write'

    audit_logs = relationship("AuditLog", back_populates="user")

class PhoneBook(Base):
    __tablename__ = "phonebook"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    phone_number = Column(String)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(String)

    user = relationship("User", back_populates="audit_logs")

# Create all tables
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI()

# Pydantic models
class PhoneBookEntry(BaseModel):
    name: str
    phone_number: str

    @validator('name')
    def validate_name(cls, value):
        # Regex for names like "First Last", "Last, First", "First Middle Last"
        pattern = r"^([a-zA-Z]+([ '-][a-zA-Z]+)*)(, [a-zA-Z]+)?$"
        if not re.match(pattern, value):
            raise ValueError("Invalid name format")
        return value.strip()

    @validator('phone_number')
    def validate_phone_number(cls, value):
        # Regex for international phone numbers with optional "+" and country code
        pattern = r"^\+?[1-9]\d{1,14}$"
        if not re.match(pattern, value):
            raise ValueError("Invalid phone number format")
        return value.strip()

    class Config:
        orm_mode = True  # Enable ORM mode

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    password: str
    role: str

# Dependency to get DB session
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Utility functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, username: str):
    return db.query(User).filter(User.username == username).first()

def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Auth dependencies
async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None or role is None:
            raise credentials_exception
        token_data = TokenData(username=username, role=role)
    except jwt.PyJWTError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def read_permission(current_user: User = Depends(get_current_user)):
    if current_user.role not in ["Read", "Read/Write"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operation not permitted")
    return current_user

async def write_permission(current_user: User = Depends(get_current_user)):
    if current_user.role != "Read/Write":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operation not permitted")
    return current_user

# Audit logging
def log_action(db: Session, user: User, action: str, details: str):
    log_entry = AuditLog(user_id=user.id, action=action, details=details)
    db.add(log_entry)
    db.commit()

# Exception handlers
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.errors()},
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

# Routes
@app.post("/users/", response_model=Token)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # For initial user creation; in production, handle user creation securely
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
        data={"sub": new_user.username, "role": new_user.role}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/token", response_model=Token)
async def login_for_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password"
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/PhoneBook/add", response_model=PhoneBookEntry)
def add_person(
    entry: PhoneBookEntry,
    db: Session = Depends(get_db),
    current_user: User = Depends(write_permission),
):
    db_entry = PhoneBook(name=entry.name, phone_number=entry.phone_number)
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    log_action(db, current_user, "add", f"Added {entry.name}")
    return db_entry

@app.get("/PhoneBook/list", response_model=List[PhoneBookEntry])
def list_phonebook(
    db: Session = Depends(get_db),
    current_user: User = Depends(read_permission),
):
    entries = db.query(PhoneBook).all()
    log_action(db, current_user, "list", "Listed phone book entries")
    return entries

@app.put("/PhoneBook/deleteByName")
def delete_by_name(
    name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(write_permission),
):
    db_entry = db.query(PhoneBook).filter(PhoneBook.name == name).first()
    if db_entry:
        db.delete(db_entry)
        db.commit()
        log_action(db, current_user, "delete", f"Deleted {name}")
        return {"message": f"Deleted {name} from the phone book"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Name not found")

@app.put("/PhoneBook/deleteByNumber")
def delete_by_number(
    phone_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(write_permission),
):
    db_entry = db.query(PhoneBook).filter(PhoneBook.phone_number == phone_number).first()
    if db_entry:
        db.delete(db_entry)
        db.commit()
        log_action(db, current_user, "delete", f"Deleted {phone_number}")
        return {"message": f"Deleted {phone_number} from the phone book"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Phone number not found")

# Optional endpoint to get audit logs (e.g., for admin users)
@app.get("/audit-logs/")
def get_audit_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(write_permission),
):
    logs = db.query(AuditLog).all()
    return logs