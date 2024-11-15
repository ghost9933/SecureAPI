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
        # Convert name to lowercase once for efficiency
        lower_name = value.lower()

        # Check for script tags or reserved keywords
        if "<script>" in lower_name or "string" in lower_name:
            raise ValueError("Invalid name format: contains prohibited substrings.")

        # Remove leading/trailing whitespace and replace multiple spaces with a single space
        # Use 'value' instead of 'name' since 'name' hasn't been defined yet
        name = re.sub(r'\s+', ' ', value.strip())

        # Compile the regular expression for acceptable characters
        # Includes both straight (') and curly (’) apostrophes, hyphens (-), commas (,), and periods (.)
        acceptable_chars = re.compile(r"^[a-zA-Z \-,'’\.]+$")

        # Check if the entire name matches the pattern (no invalid special characters)
        if not acceptable_chars.fullmatch(name):
            raise ValueError("Invalid name format: contains invalid characters.")

        # Split the name into words
        words = name.split()

        # Check for maximum number of words
        if len(words) > 3:
            raise ValueError("Invalid name format: exceeds maximum number of words (3).")

        # Check for single occurrences of special characters per word segment
        for word in words:
            if any(word.count(char) > 1 for char in ["-", "'", "’", ","]):
                raise ValueError("Invalid name format: multiple special characters in a word.")

        # Name validation successful
        return name   
    
    
    
     # Return the cleaned and validated name

    
        # # Define allowed characters within names or single initials with an optional dot
        # name_part = r"(?:[A-Za-zÀ-ÖØ-öø-ÿ'’‘\-]+|[A-Za-z]\.)"
        
        # # Define patterns for valid formats
        # single_word = fr"^{name_part}$"  # Single name (e.g., "Cher")
        # two_words = fr"^{name_part}\s+{name_part}$"  # First Last (e.g., "Bruce Schneier")
        # three_words = fr"^{name_part}\s+{name_part}\s+{name_part}$"  # First Middle Last or Last, First Middle
        # last_comma_first_middle = fr"^{name_part},\s+{name_part}(?:\s+{name_part})?$"  # Last, First [Middle]

        # # Combined pattern
        # pattern = fr"^(?:{single_word}|{two_words}|{three_words}|{last_comma_first_middle})$"

        # # Check if the input matches one of the valid patterns
        # if not re.match(pattern, value, flags=re.UNICODE):
        #     raise ValueError("Invalid name format")

        # # Ensure no multiple hyphens or apostrophes within a single part of the name
        # for part in re.split(r"[\s,]+", value):
        #     # Disallow consecutive special characters
        #     if re.search(r"[’'‘\-]{2,}", part):
        #         raise ValueError("Invalid name format")
            
        #     # Allow at most one hyphen or apostrophe per name part
        #     if len(re.findall(r"[’'‘\-]", part)) > 1:
        #         raise ValueError("Invalid name format")

        # # Check the total number of name components (to restrict to max 3 words)
        # name_parts = re.split(r"[\s,]+", value)
        # if len(name_parts) > 3:
        #     raise ValueError("Invalid name format")

        # return value.strip()

    @validator('phone_number')
    def validate_phone_number(cls, value):

        phone_str = str(value).strip()

        # a. Check for presence of script tags (basic XSS protection)
        if re.search(r"<\s*script.*?>", phone_str, re.IGNORECASE):
            raise ValueError("Invalid phone number: Contains script tags")

        # b. Reject if any alphabetic characters are present
        if re.search(r"[A-Za-z]", phone_str):
            raise ValueError("Invalid phone number: Contains alphabetic characters")

        # c. Reject phone numbers containing disallowed characters
        if re.search(r"[^\d\s\-\.\+\(\)]", phone_str):
            raise ValueError("Invalid phone number: Contains disallowed characters")

        # d. Reject phone numbers with extensions or additional text
        if re.search(r"(ext|x|extension)", phone_str, re.IGNORECASE):
            raise ValueError("Invalid phone number: Contains extension")

        # e. Check for continuous 10-digit numbers without separators
        if re.fullmatch(r"\d{10}", phone_str):
            raise ValueError("Invalid phone number: Unformatted 10-digit sequence")

        # Define regex patterns for valid phone number formats
        patterns = [
            r"^\d{5}$",  # 5-digit numbers
            r"^\d{3}-\d{4}$",  # 7-digit numbers with hyphen
            r"^\(?[2-9]\d{2}\)?[-.\s]?\d{3}[-.\s]?\d{4}$",  # North American numbers with area code
            r"^(?:\+1\s?|1\s?|011\s\d{1,3}\s?)\(?\d{2,3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$",  # International with prefix
            r"^\+(?!01\b)\d{1,3}\s?\(?\d{2,3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$",  # International with "+"
            r"^\d{5}[-.\s]?\d{5}$"  # Two groups of 5 digits
        ]

        # Compile the patterns for efficiency
        compiled_patterns = [re.compile(pattern) for pattern in patterns]

        # Check if the phone number matches any of the valid patterns
        for pattern in compiled_patterns:
            if pattern.fullmatch(phone_str):
                # Additional checks based on specific rules
                if phone_str.startswith('('):
                    area_code = re.findall(r"\((\d{3})\)", phone_str)
                    if area_code and area_code[0].startswith(('0', '1')):
                        raise ValueError("Invalid phone number: Area code cannot start with '0' or '1'")

                if phone_str.startswith('+'):
                    country_code = re.findall(r"^\+(\d{1,3})", phone_str)
                    if country_code and country_code[0] == '01':
                        raise ValueError("Invalid phone number: Country code cannot be '01'")

                invalid_area_codes = ['000', '001']
                if phone_str.startswith('('):
                    area_code = re.findall(r"\((\d{3})\)", phone_str)
                    if area_code and area_code[0] in invalid_area_codes:
                        raise ValueError("Invalid phone number: Contains invalid area code")

                # If all checks passed, return the validated phone number
                return phone_str

        # If none of the patterns matched
        raise ValueError("Invalid phone number format")

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
