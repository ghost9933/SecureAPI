# schemas/user.py

from pydantic import BaseModel, validator
import re

class UserCreate(BaseModel):
    username: str
    password: str
    role: str

    @validator('role')
    def validate_role(cls, value):
        if value not in ["Read", "Read/Write"]:
            raise ValueError("Invalid role")
        return value
