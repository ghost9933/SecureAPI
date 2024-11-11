# database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

from config import DATABASE_URL

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=True, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for declarative class definitions
Base = declarative_base()

def get_db():
    """
    Dependency that provides a session to the database.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
