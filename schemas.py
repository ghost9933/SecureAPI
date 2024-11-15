# schemas.py

from pydantic import BaseModel, validator
from typing import List, Optional
import re

class PhoneBookEntry(BaseModel):
    name: str
    phone_number: str

    @validator('name')
    def validate_name(cls, value):

        lower_name = value.lower()

        # Check for script tags or reserved keywords
        if "<script>" in lower_name or "string" in lower_name:
            raise ValueError("Invalid name format: contains prohibited substrings.")
        # whitespace at edges
        name = re.sub(r'\s+', ' ', value.strip())

        # special chars
        acceptable_chars = re.compile(r"^[a-zA-Z \-,'’\.]+$")


        if not acceptable_chars.fullmatch(name):
            raise ValueError("Invalid name format: contains invalid characters.")

        # Split the name into words
        words = name.split()


        if len(words) > 3:
            raise ValueError("Invalid name format: exceeds maximum number of words (3).")

        for word in words:
            if any(word.count(char) > 1 for char in ["-", "'", "’", ","]):
                raise ValueError("Invalid name format: multiple special characters in a word.")

        return name   

    @validator('phone_number')
    def validate_phone_number(cls, value):

        phone_str = str(value).strip()


        if re.search(r"<\s*script.*?>", phone_str, re.IGNORECASE):
            raise ValueError("Invalid phone number: Contains script tags")


        if re.search(r"[A-Za-z]", phone_str):
            raise ValueError("Invalid phone number: Contains alphabetic characters")

        if re.search(r"[^\d\s\-\.\+\(\)]", phone_str):
            raise ValueError("Invalid phone number: Contains disallowed characters")

        if re.search(r"(ext|x|extension)", phone_str, re.IGNORECASE):
            raise ValueError("Invalid phone number: Contains extension")

        if re.fullmatch(r"\d{10}", phone_str):
            raise ValueError("Invalid phone number: Unformatted 10-digit sequence")


        patterns = [
            r"^\d{5}$",  # 5-digit numbers
            r"^\d{3}-\d{4}$",  # 7-digit numbers with hyphen
            r"^\(?[2-9]\d{2}\)?[-.\s]?\d{3}[-.\s]?\d{4}$",  # North American numbers with area code
            r"^(?:\+1\s?|1\s?|011\s\d{1,3}\s?)\(?\d{2,3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$",  # International with prefix
            r"^\+(?!01\b)\d{1,3}\s?\(?\d{2,3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$",  # International with "+"
            r"^\d{5}[-.\s]?\d{5}$"  # Two groups of 5 digits
        ]


        compiled_patterns = [re.compile(pattern) for pattern in patterns]

        for pattern in compiled_patterns:
            if pattern.fullmatch(phone_str):
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


                return value.strip()


        raise ValueError("Invalid phone number format")

    class Config:
        orm_mode = True  

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None
    token_version: Optional[int] = 0  
    
class UserCreate(BaseModel):
    username: str
    password: str
    role: str
