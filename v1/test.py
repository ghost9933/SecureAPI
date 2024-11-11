# tests/test_app.py

import pytest
from fastapi.testclient import TestClient
from app import app
from jose import jwt
from config import SECRET_KEY, ALGORITHM

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

client = TestClient(app)

def get_token(username: str, role: str) -> str:
    """
    Generates a JWT token for a given user with a specified role.
    
    Args:
        username (str): The username of the user.
        role (str): The role of the user (e.g., 'read', 'readwrite').

    Returns:
        str: A JWT token as a string.
    """
    to_encode = {"sub": username, "role": role}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Fixtures for tokens
@pytest.fixture
def read_token() -> str:
    """
    Fixture to provide a JWT token for a user with 'read' permissions.
    
    Returns:
        str: A JWT token as a string.
    """
    return get_token("readuser", "read")

@pytest.fixture
def write_token() -> str:
    """
    Fixture to provide a JWT token for a user with 'readwrite' permissions.
    
    Returns:
        str: A JWT token as a string.
    """
    return get_token("writeuser", "readwrite")

# Test valid inputs
def test_add_person_valid(write_token):
    """
    Test adding a person with valid name and phone number.
    
    Args:
        write_token (str): JWT token with 'readwrite' permissions.
    """
    headers = {"Authorization": f"Bearer {write_token}"}
    response = client.post(
        "/PhoneBook/add",
        json={"name": "Bruce Schneier", "phoneNumber": "(703)111-2121"},
        headers=headers
    )
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    assert response.json() == {"message": "Person added successfully"}, "Response message mismatch"

# Test invalid name
def test_add_person_invalid_name(write_token):
    """
    Test adding a person with an invalid name format.
    
    Args:
        write_token (str): JWT token with 'readwrite' permissions.
    """
    headers = {"Authorization": f"Bearer {write_token}"}
    response = client.post(
        "/PhoneBook/add",
        json={"name": "L33t Hacker", "phoneNumber": "(703)111-2121"},
        headers=headers
    )
    assert response.status_code == 422, f"Expected status code 422, got {response.status_code}"
    assert response.json()["detail"][0]["msg"] == "Invalid name format", "Expected 'Invalid name format' error"

# Test invalid phone number
def test_add_person_invalid_phone(write_token):
    """
    Test adding a person with an invalid phone number format.
    
    Args:
        write_token (str): JWT token with 'readwrite' permissions.
    """
    headers = {"Authorization": f"Bearer {write_token}"}
    response = client.post(
        "/PhoneBook/add",
        json={"name": "Bruce Schneier", "phoneNumber": "123"},
        headers=headers
    )
    assert response.status_code == 422, f"Expected status code 422, got {response.status_code}"
    assert response.json()["detail"][0]["msg"] == "Invalid phone number format", "Expected 'Invalid phone number format' error"

# Test listing phonebook entries with read permissions
def test_list_phonebook_read(read_token):
    """
    Test listing all phonebook entries with 'read' permissions.
    
    Args:
        read_token (str): JWT token with 'read' permissions.
    """
    headers = {"Authorization": f"Bearer {read_token}"}
    response = client.get("/PhoneBook/list", headers=headers)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    assert isinstance(response.json(), list), "Expected response to be a list"

# Test unauthorized access when adding a person with read-only permissions
def test_add_person_unauthorized(read_token):
    """
    Test adding a person with 'read' permissions, which should be unauthorized.
    
    Args:
        read_token (str): JWT token with 'read' permissions.
    """
    headers = {"Authorization": f"Bearer {read_token}"}
    response = client.post(
        "/PhoneBook/add",
        json={"name": "Cher", "phoneNumber": "123-1234"},
        headers=headers
    )
    assert response.status_code == 403, f"Expected status code 403, got {response.status_code}"
    assert response.json()["detail"] == "Operation not permitted", "Expected 'Operation not permitted' error"

# Test deleting a non-existent person
def test_delete_nonexistent_person(write_token):
    """
    Test deleting a person who does not exist in the database.
    
    Args:
        write_token (str): JWT token with 'readwrite' permissions.
    """
    headers = {"Authorization": f"Bearer {write_token}"}
    response = client.put(
        "/PhoneBook/deleteByName",
        params={"name": "Non Existent"},
        headers=headers
    )
    assert response.status_code == 404, f"Expected status code 404, got {response.status_code}"
    assert response.json()["detail"] == "Person not found in the database", "Expected 'Person not found in the database' error"
