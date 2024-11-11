
**Explanation of Directories:**
```
SecureAPI/
├── app.py
├── models/
│   ├── __init__.py
│   ├── user.py
│   ├── phonebook.py
│   └── audit_log.py
├── schemas/
│   ├── __init__.py
│   ├── user.py
│   ├── phonebook.py
│   └── token.py
├── database.py
├── auth/
│   ├── __init__.py
│   └── auth.py
├── routers/
│   ├── __init__.py
│   ├── users.py
│   ├── phonebook.py
│   └── audit_logs.py
├── utils/
│   ├── __init__.py
│   └── utils.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env
└── README.md
```

**Files:**

- **`app.py`**: The main entry point of your FastAPI application.
- **`models/`**: Contains SQLAlchemy ORM models.
- **`schemas/`**: Contains Pydantic models (data validation and serialization).
- **`database.py`**: Handles database connection and session management.
- **`auth/`**: Manages authentication-related functionalities.
- **`routers/`**: Contains API route handlers grouped by functionality.
- **`utils/`**: Contains utility functions and helpers.
- **`requirements.txt`**: Lists Python dependencies.
- **`Dockerfile`** & **`docker-compose.yml`**: For containerization and orchestration.
- **`.env`**: Stores environment variables.
- **`README.md`**: Project documentation.

---

# Secure PhoneBook API

A secure and modular FastAPI application for managing a phonebook with user authentication and audit logging.

## Features

- **User Authentication**: JWT-based authentication with role-based access control (`Read` and `Read/Write`).
- **CRUD Operations**: Add, list, and delete phonebook entries.
- **Audit Logging**: Track user actions for auditing purposes.
- **Dockerized**: Easily deployable using Docker and Docker Compose.
- **Environment Variables**: Securely manage configurations using a `.env` file.

## Getting Started

### Prerequisites

- [Python 3.9+](https://www.python.org/downloads/)
- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/SecureAPI.git
   cd SecureAPI
   ```

2. **Create and Activate Virtual Environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**

   Create a `.env` file in the project root:

   ```env
   SECRET_KEY=your_secure_secret_key_here
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   DATABASE_URL=sqlite:///./data/phonebook.db
   ```

5. **Run the Application:**

   ```bash
   uvicorn app:app --reload
   ```

   Access the API documentation at [http://localhost:8000/docs](http://localhost:8000/docs).

### Using Docker

1. **Build the Docker Image:**

   ```bash
   docker-compose build
   ```

2. **Run the Container:**

   ```bash
   docker-compose up -d
   ```

3. **Access the Application:**

   Visit [http://localhost:8000/docs](http://localhost:8000/docs) to interact with the API.

4. **Stopping the Container:**

   ```bash
   docker-compose down
   ```

## API Endpoints

### Authentication

- **Create User**

  - **URL:** `/users/`
  - **Method:** `POST`
  - **Body:**
    ```json
    {
      "username": "user1",
      "password": "securepassword",
      "role": "Read/Write"
    }
    ```
  - **Response:**
    ```json
    {
      "access_token": "jwt_token_here",
      "token_type": "bearer"
    }
    ```

- **Login**

  - **URL:** `/token`
  - **Method:** `POST`
  - **Form Data:**
    - `username`: `user1`
    - `password`: `securepassword`
  - **Response:**
    ```json
    {
      "access_token": "jwt_token_here",
      "token_type": "bearer"
    }
    ```

### PhoneBook

- **Add Entry**

  - **URL:** `/PhoneBook/add`
  - **Method:** `POST`
  - **Headers:** `Authorization: Bearer <token>`
  - **Body:**
    ```json
    {
      "name": "John Doe",
      "phone_number": "+1234567890"
    }
    ```
  - **Response:**
    ```json
    {
      "name": "John Doe",
      "phone_number": "+1234567890"
    }
    ```

- **List Entries**

  - **URL:** `/PhoneBook/list`
  - **Method:** `GET`
  - **Headers:** `Authorization: Bearer <token>`
  - **Response:**
    ```json
    [
      {
        "name": "John Doe",
        "phone_number": "+1234567890"
      },
      {
        "name": "Jane Smith",
        "phone_number": "+0987654321"
      }
    ]
    ```

- **Delete by Name**

  - **URL:** `/PhoneBook/deleteByName`
  - **Method:** `PUT`
  - **Headers:** `Authorization: Bearer <token>`
  - **Query Params:** `name=John%20Doe`
  - **Response:**
    ```json
    {
      "message": "Deleted John Doe from the phone book"
    }
    ```

- **Delete by Number**

  - **URL:** `/PhoneBook/deleteByNumber`
  - **Method:** `PUT`
  - **Headers:** `Authorization: Bearer <token>`
  - **Query Params:** `phone_number=+1234567890`
  - **Response:**
    ```json
    {
      "message": "Deleted +1234567890 from the phone book"
    }
    ```

### Audit Logs

- **Get Audit Logs**

  - **URL:** `/audit-logs/`
  - **Method:** `GET`
  - **Headers:** `Authorization: Bearer <token>`
  - **Response:**
    ```json
    [
      {
        "id": 1,
        "user_id": 1,
        "action": "add",
        "timestamp": "2023-11-10T12:34:56.789Z",
        "details": "Added John Doe"
      },
      {
        "id": 2,
        "user_id": 1,
        "action": "list",
        "timestamp": "2023-11-10T12:35:00.123Z",
        "details": "Listed phone book entries"
      }
    ]
    ```

## **4. Running and Testing the Modularized Application**

### **A. Running Locally**

1. **Ensure the `data/` Directory Exists:**

   ```bash
   mkdir data
   ```

2. **Run the Application:**

   ```bash
   uvicorn app:app --reload
   ```

3. **Access API Documentation:**

   Navigate to [http://localhost:8000/docs](http://localhost:8000/docs) to interact with the API using Swagger UI.

### **B. Running with Docker**

1. **Build the Docker Image:**

   ```bash
   docker-compose build
   ```

2. **Start the Docker Container:**

   ```bash
   docker-compose up -d
   ```

3. **Access the Application:**

   Visit [http://localhost:8000/docs](http://localhost:8000/docs).

4. **Verify Database Persistence:**

   - Add a phonebook entry.
   - Stop the Docker container: `docker-compose down`.
   - Start the container again: `docker-compose up -d`.
   - List entries to ensure data persists.
