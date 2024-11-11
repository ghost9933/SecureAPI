# routers/users.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas.user import UserCreate
from schemas.token import Token
from auth.auth import get_db, get_password_hash, create_access_token
from models.user import User
from utils.logging_config import setup_logging

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

# Initialize logger
logger = setup_logging()

@router.post("/", response_model=Token)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    logger.info(f"Attempting to create user: {user.username}")
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        logger.warning(f"User creation failed: Username '{user.username}' already exists.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    hashed_password = get_password_hash(user.password)
    new_user = User(
        username=user.username,
        hashed_password=hashed_password,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    access_token = create_access_token(
        data={"sub": new_user.username, "role": new_user.role}
    )
    logger.info(f"User '{user.username}' created successfully.")
    return {"access_token": access_token, "token_type": "bearer"}
