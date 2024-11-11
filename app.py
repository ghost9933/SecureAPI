# app.py

from fastapi import FastAPI
from database import engine, Base
from routers import users, token, phonebook, audit_logs
from utils.logging_config import setup_logging

# Initialize logging
logger = setup_logging()

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Secure PhoneBook API",
    description="A secure and modular FastAPI application for managing a phonebook with user authentication and audit logging.",
    version="1.0.0",
)

# Include routers
app.include_router(users.router)
app.include_router(token.router)
app.include_router(phonebook.router)
app.include_router(audit_logs.router)

# Optional: Log when the application starts
@app.on_event("startup")
async def startup_event():
    logger.info("Application startup complete.")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown initiated.")
