
# SecureAPI Application

This repository contains a Python application deployed with Docker, utilizing **Uvicorn** and **Python 3.9-slim**. It provides robust features for secure API interactions, including authentication, phone number validation, and name validation to mitigate XSS vulnerabilities.

---

## Features

- **Authentication and Authorization**: Token-based user role management.
- **Phone Number Validation**: Ensures correct format and prevents input errors.
- **Name Validation**: Mitigates security risks like XSS.
- **Permission Handling**: Correctly distinguishes read and write permissions.
- **Database Integrity**: Resets and cleans up the database after each test.

---

## Prerequisites

Before running the application, ensure you have the following installed:

- Docker and Docker Compose
- Python 3.9+ (for local environment testing)
- `pip` (Python package manager)

---

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```

2. **Create a Python Virtual Environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the Virtual Environment**
   - On Windows (Command Prompt):
     ```bash
     venv\Scripts\activate
     ```
   - On Windows (PowerShell):
     ```bash
     .\venv\Scripts\Activate.ps1
     ```
   - On Linux/MacOS:
     ```bash
     source venv/bin/activate
     ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Build the Docker Images**
   ```bash
   docker-compose build
   ```

6. **Run the Application**
   ```bash
   docker-compose up -d
   ```

   - The application will run on **port 8000** by default. Update the `docker-compose.yml` file if the port is unavailable.

---

## Testing Instructions

The repository includes automated test scripts to validate the application's functionality.

### Run Tests with Docker

1. **Token Generation and Invalidations**
   ```bash
   docker exec -it secureapi_app python /app/tests/creds_tests.py
   ```

2. **Name Validation Tests**
   ```bash
   docker exec -it secureapi_app python /app/tests/name_test.py
   ```

3. **Phone Number Validation Tests**
   ```bash
   docker exec -it secureapi_app python /app/tests/phone_test.py
   ```

4. **Unit Tests for All Endpoints**
   ```bash
   docker exec -it secureapi_app python /app/tests/unit_tests.py
   ```

---

## Troubleshooting

- **Port 8000 Unavailable**: 
  Modify the `docker-compose.yml` file to change the port mapping, e.g., `- "8001:8000"`, and restart the application.

- **Database Issues**:
  Ensure database services are correctly initialized and running in the `docker-compose.yml`.

- **Environment Activation**:
  If the virtual environment fails to activate, check your terminal's permissions or use an elevated terminal.

