# routers/users.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas.user import UserCreate
from schemas.token import Token
from auth.auth import get_db, get_password_hash, authenticate_user, create_access_token
from models.user import User

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.post("/", response_model=Token)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
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
    return {"access_token": access_token, "token_type": "bearer"}
