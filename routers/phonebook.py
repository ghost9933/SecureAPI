# routers/phonebook.py

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from schemas.phonebook import PhoneBookEntry
from models.phonebook import PhoneBook
from auth.auth import get_db
from models.user import User
from auth.auth import credentials_exception
from fastapi.security import OAuth2PasswordBearer
from schemas.token import TokenData
from auth.auth import decode_access_token
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter(
    prefix="/PhoneBook",
    tags=["phonebook"],
)

# Dependency to get current user
from auth.auth import decode_access_token, credentials_exception
from auth.auth import get_db

from fastapi import Security
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        token_data = decode_access_token(token)
    except:
        raise credentials_exception
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

def read_permission(current_user: User = Depends(get_current_user)):
    if current_user.role not in ["Read", "Read/Write"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation not permitted"
        )
    return current_user

def write_permission(current_user: User = Depends(get_current_user)):
    if current_user.role != "Read/Write":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation not permitted"
        )
    return current_user

from models.audit_log import AuditLog

def log_action(db: Session, user: User, action: str, details: str):
    log_entry = AuditLog(user_id=user.id, action=action, details=details)
    db.add(log_entry)
    db.commit()

@router.post("/add", response_model=PhoneBookEntry)
def add_person(
    entry: PhoneBookEntry,
    db: Session = Depends(get_db),
    current_user: User = Depends(write_permission),
):
    try:
        db_entry = PhoneBook(name=entry.name, phone_number=entry.phone_number)
        db.add(db_entry)
        db.commit()
        db.refresh(db_entry)
        log_action(db, current_user, "add", f"Added {entry.name}")
        return db_entry
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/list", response_model=List[PhoneBookEntry])
def list_phonebook(
    db: Session = Depends(get_db),
    current_user: User = Depends(read_permission),
):
    try:
        entries = db.query(PhoneBook).all()
        log_action(db, current_user, "list", "Listed phone book entries")
        return entries
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.put("/deleteByName")
def delete_by_name(
    name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(write_permission),
):
    try:
        db_entry = db.query(PhoneBook).filter(PhoneBook.name == name).first()
        if db_entry:
            db.delete(db_entry)
            db.commit()
            log_action(db, current_user, "delete", f"Deleted {name}")
            return {"message": f"Deleted {name} from the phone book"}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Name not found")
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.put("/deleteByNumber")
def delete_by_number(
    phone_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(write_permission),
):
    try:
        db_entry = db.query(PhoneBook).filter(PhoneBook.phone_number == phone_number).first()
        if db_entry:
            db.delete(db_entry)
            db.commit()
            log_action(db, current_user, "delete", f"Deleted {phone_number}")
            return {"message": f"Deleted {phone_number} from the phone book"}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Phone number not found")
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")
