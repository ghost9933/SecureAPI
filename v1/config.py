# config.py

import os

SECRET_KEY = os.getenv("SECRET_KEY", "your_default_secret_key")  # Use a default for development
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./phonebook.db")
