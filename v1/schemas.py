# schemas.py

from pydantic import BaseModel, validator,EmailStr
import re
from typing import Optional

# Regular expressions for validation
NAME_REGEX = re.compile(
    r"^(?:(?:[A-Za-z]+(?:[-'][A-Za-z]+)*)\s?)+(?:,?\s?(?:[A-Za-z]+(?:[-'][A-Za-z]+)*))?$"
)

PHONE_REGEX = re.compile(
    r"^(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,3}\)?[\s.-]?)?\d{3,4}[\s.-]?\d{4}$"
)

class Person(BaseModel):
    name: str
    phoneNumber: str

    @validator('name')
    def validate_name(cls, v):
        if not NAME_REGEX.match(v):
            raise ValueError('Invalid name format')
        return v

    @validator('phoneNumber')
    def validate_phone(cls, v):
        if not PHONE_REGEX.match(v):
            raise ValueError('Invalid phone number format')
        return v

class User(BaseModel):
    username: str
    full_name: str
    role: str

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None


class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr
    role: str = "read"