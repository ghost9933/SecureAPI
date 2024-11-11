# app.py

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from db import engine, Base
from Router import phonebook
from auth import create_access_token
from schemas import Token,UserCreate
from loging import setup_logging
from auth import oauth2_scheme
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from auth import authenticate_user
from fastapi.responses import JSONResponse

from passlib.context import CryptContext
from models import UserModel 


from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Initialize logging
setup_logging()

# Create the database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Secure PhoneBook API",
    description="A secure API for managing a phone book with authentication and audit logging.",
    version="1.0.0"
)

# Add CORS middleware if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the phonebook router
app.include_router(phonebook.router)

# Import necessary modules for authentication
from auth import create_access_token, authenticate_user
from config import ACCESS_TOKEN_EXPIRE_MINUTES



@app.post("/signup", response_model=dict, tags=["Authentication"])
def signup(user: UserCreate, db: Session = Depends(get_db)):
    """
    Endpoint to register a new user.
    """
    # Check if user already exists
    existing_user = db.query(UserModel).filter_by(username=user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Hash the password
    hashed_password = pwd_context.hash(user.password)
    
    # Create new user record
    new_user = UserModel(
        username=user.username,
        hashed_password=hashed_password,
        email=user.email,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "User created successfully"}

@app.post("/token", response_model=Token, tags=["Authentication"])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Endpoint to authenticate a user and return a JWT token.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# routers/phonebook.py


from schemas import Person
from models import PhoneBook
from db import get_db
from auth import require_role, User
from loging import log_action

router = APIRouter()

@router.get("/PhoneBook/list", tags=["PhoneBook"])
def list_phonebook(current_user: User = Depends(require_role(["read", "readwrite"])), db: Session = Depends(get_db)):
    phonebook = db.query(PhoneBook).all()
    log_action("LIST", f"User {current_user.username} listed all entries")
    return phonebook

@router.post("/PhoneBook/add", tags=["PhoneBook"])
def add_person(person: Person, current_user: User = Depends(require_role(["readwrite"])), db: Session = Depends(get_db)):
    existing_person = db.query(PhoneBook).filter_by(phone_number=person.phoneNumber).first()
    if existing_person:
        raise HTTPException(status_code=400, detail="Person already exists in the database")
    
    new_person = PhoneBook(full_name=person.name, phone_number=person.phoneNumber)
    db.add(new_person)
    db.commit()
    log_action("ADD", f"User {current_user.username} added {person.name}")
    return {"message": "Person added successfully"}

@router.put("/PhoneBook/deleteByName", tags=["PhoneBook"])
def delete_by_name(name: str, current_user: User = Depends(require_role(["readwrite"])), db: Session = Depends(get_db)):
    person = db.query(PhoneBook).filter_by(full_name=name).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found in the database")
    
    db.delete(person)
    db.commit()
    log_action("DELETE_BY_NAME", f"User {current_user.username} deleted {name}")
    return {"message": "Person deleted successfully"}

@router.put("/PhoneBook/deleteByNumber", tags=["PhoneBook"])
def delete_by_number(number: str, current_user: User = Depends(require_role(["readwrite"])), db: Session = Depends(get_db)):
    person = db.query(PhoneBook).filter_by(phone_number=number).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found in the database")
    
    db.delete(person)
    db.commit()
    log_action("DELETE_BY_NUMBER", f"User {current_user.username} deleted {number}")
    return {"message": "Person deleted successfully"}
