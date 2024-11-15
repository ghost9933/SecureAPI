from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from models import Base, AuditLog
from database import engine
from schemas import PhoneBookEntry, Token, UserCreate
from controllers import auth, phonebook
from dependencies import get_db, read_permission, write_permission
from controllers.phonebook import log_action
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.security import OAuth2PasswordRequestForm  # Correct import

# Create 
Base.metadata.create_all(bind=engine)


app = FastAPI()


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


@app.post("/users/", response_model=Token)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return auth.create_new_user(db, user)


@app.post("/token", response_model=Token)
def login_for_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),  
):
    return auth.login_user(db, form_data.username, form_data.password)


@app.post("/PhoneBook/add", response_model=PhoneBookEntry)
def add_person(
    entry: PhoneBookEntry,
    db: Session = Depends(get_db),
    current_user: auth.User = Depends(write_permission),  
):
    return phonebook.add_person(db, entry, current_user)


@app.get("/PhoneBook/list", response_model=List[PhoneBookEntry])
def list_phonebook_entries(
    db: Session = Depends(get_db),
    current_user: auth.User = Depends(read_permission),  
):
    return phonebook.list_phonebook(db, current_user)


@app.put("/PhoneBook/deleteByName")
def delete_by_name(
    name: str,
    db: Session = Depends(get_db),
    current_user: auth.User = Depends(write_permission), 
):
    return phonebook.delete_by_name(db, name, current_user)


@app.put("/PhoneBook/deleteByNumber")
def delete_by_number(
    phone_number: str,
    db: Session = Depends(get_db),
    current_user: auth.User = Depends(write_permission), 
):
    return phonebook.delete_by_number(db, phone_number, current_user)


@app.get("/audit-logs/")
def get_audit_logs(
    db: Session = Depends(get_db),
    current_user: auth.User = Depends(write_permission),  
):
    logs = db.query(AuditLog).all()
    return logs


@app.post("/revoke-tokens/")
def revoke_tokens(
    db: Session = Depends(get_db),
    current_user: auth.User = Depends(write_permission),  
):
    current_user.token_version += 1
    db.commit()
    log_action(db, current_user, "revoke", "Revoked all tokens")
    return {"message": "All tokens have been revoked"}
