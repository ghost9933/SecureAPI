from sqlalchemy.orm import Session
from models import PhoneBook, AuditLog, User
from schemas import PhoneBookEntry
from fastapi import HTTPException, status

def add_person(db: Session, entry: PhoneBookEntry, current_user: User):
    db_entry = PhoneBook(name=entry.name, phone_number=entry.phone_number)
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    log_action(db, current_user, "add", f"Added {entry.name}")
    return db_entry

def list_phonebook(db: Session, current_user: User):
    entries = db.query(PhoneBook).all()
    log_action(db, current_user, "list", "Listed phone book entries")
    return entries

def delete_by_name(db: Session, name: str, current_user: User):
    db_entry = db.query(PhoneBook).filter(PhoneBook.name == name).first()
    if db_entry:
        db.delete(db_entry)
        db.commit()
        log_action(db, current_user, "delete", f"Deleted {name}")
        return {"message": f"Deleted {name} from the phone book"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Name not found")

def delete_by_number(db: Session, phone_number: str, current_user: User):
    db_entry = db.query(PhoneBook).filter(PhoneBook.phone_number == phone_number).first()
    if db_entry:
        db.delete(db_entry)
        db.commit()
        log_action(db, current_user, "delete", f"Deleted {phone_number}")
        return {"message": f"Deleted {phone_number} from the phone book"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Phone number not found")

def log_action(db: Session, user: User, action: str, details: str):
    log_entry = AuditLog(user_id=user.id, action=action, details=details)
    db.add(log_entry)
    db.commit()
