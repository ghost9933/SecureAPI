# schemas/phonebook.py

from pydantic import BaseModel, validator
import re

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
