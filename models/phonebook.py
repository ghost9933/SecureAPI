# models/phonebook.py

from sqlalchemy import Column, Integer, String
from database import Base

class PhoneBook(Base):
    __tablename__ = "phonebook"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    phone_number = Column(String, nullable=False)
