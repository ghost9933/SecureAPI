import http.client
import json
from datetime import datetime, timedelta

# API host and endpoints
HOST = "127.0.0.1"
PORT = 8000
USER_CREATION_ENDPOINT = "/users/"
TOKEN_ENDPOINT = "/token"
ADD_PERSON_ENDPOINT = "/PhoneBook/add"
DELETE_BY_NAME_ENDPOINT = "/PhoneBook/deleteByName"

# User credentials for read-only and read/write users
READ_USER = "read_user"
READ_WRITE_USER = "rw_user"
PASSWORD = "password123"

# Helper functions
def create_user(username, password, role):
    conn = http.client.HTTPConnection(HOST, PORT)
    headers = {"Content-Type": "application/json"}
    body = json.dumps({"username": username, "password": password, "role": role})
    
    conn.request("POST", USER_CREATION_ENDPOINT, body, headers)
    response = conn.getresponse()
    response_data = response.read().decode()
    
    if response.status == 200:
        print(f"[PASS] User '{username}' with role '{role}' created successfully.")
    else:
        print(f"[FAIL] Failed to create user '{username}' with role '{role}'. Response: {response_data}")
    
    conn.close()

def get_access_token(username, password):
    conn = http.client.HTTPConnection(HOST, PORT)
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    body = f"username={username}&password={password}"
    
    conn.request("POST", TOKEN_ENDPOINT, body, headers)
    response = conn.getresponse()
    response_data = response.read().decode()
    
    if response.status == 200:
        token_data = json.loads(response_data)
        access_token = token_data.get("access_token")
        print(f"[INFO] Access token for '{username}' retrieved successfully.")
        conn.close()
        return access_token
    else:
        print(f"[ERROR] Failed to get access token for '{username}'. Response: {response_data}")
    
    conn.close()
    return None

def test_read_user_permissions(token):
    # Attempt to add an entry with a read-only user
    conn = http.client.HTTPConnection(HOST, PORT)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    body = json.dumps({"name": "Test User", "phone_number": "123-4567"})
    
    conn.request("POST", ADD_PERSON_ENDPOINT, body, headers)
    response = conn.getresponse()
    
    if response.status == 400:
        print("[PASS] Read-only user was correctly prevented from adding an entry.")
    else:
        print("[FAIL] Read-only user was allowed to add an entry. Status:", response.status)
    
    conn.close()
    
    # Attempt to delete an entry with a read-only user
    conn = http.client.HTTPConnection(HOST, PORT)
    headers = {"Authorization": f"Bearer {token}"}
    
    conn.request("PUT", f"{DELETE_BY_NAME_ENDPOINT}?name=Test%20User", headers=headers)
    response = conn.getresponse()
    
    if response.status == 400:
        print("[PASS] Read-only user was correctly prevented from deleting an entry.")
    else:
        print("[FAIL] Read-only user was allowed to delete an entry. Status:", response.status)
    
    conn.close()

def test_token_invalidation(username, password):
    # Obtain the first token
    token1 = get_access_token(username, password)
    if not token1:
        print(f"[ERROR] Could not get first token for {username}")
        return

    # Obtain a second token (which should invalidate the first token)
    token2 = get_access_token(username, password)
    if not token2:
        print(f"[ERROR] Could not get second token for {username}")
        return

    # Attempt to use the first token (expected to be invalid)
    conn = http.client.HTTPConnection(HOST, PORT)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token1}",
    }
    body = json.dumps({"name": "Invalid Test", "phone_number": "123-4567"})
    
    conn.request("POST", ADD_PERSON_ENDPOINT, body, headers)
    response = conn.getresponse()
    
    if response.status == 400:
        print("[PASS] First token was correctly invalidated after obtaining a second token.")
    else:
        print("[FAIL] First token is still valid, expected invalidation. Status:", response.status)
    
    conn.close()

    # Verify that the second token is still valid
    conn = http.client.HTTPConnection(HOST, PORT)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token2}",
    }
    
    conn.request("POST", ADD_PERSON_ENDPOINT, body, headers)
    response = conn.getresponse()
    
    if response.status == 200:
        print("[PASS] Second token is valid and usable.")
    else:
        print("[FAIL] Second token is not working as expected. Status:", response.status)
    
    conn.close()

# Main testing function
def main():
    # Create users for testing
    create_user(READ_USER, PASSWORD, "Read")
    create_user(READ_WRITE_USER, PASSWORD, "Read/Write")
    
    # Get tokens for each user
    read_token = get_access_token(READ_USER, PASSWORD)
    rw_token = get_access_token(READ_WRITE_USER, PASSWORD)
    
    if not read_token or not rw_token:
        print("[ERROR] Could not obtain tokens for users, aborting tests.")
        return
    
    # Test read-only user permissions
    print("\n[INFO] Testing permissions for read-only user")
    test_read_user_permissions(read_token)
    
    # Test token invalidation for both read-only and read/write users
    print("\n[INFO] Testing token invalidation for read-only user")
    test_token_invalidation(READ_USER, PASSWORD)
    
    print("\n[INFO] Testing token invalidation for read/write user")
    test_token_invalidation(READ_WRITE_USER, PASSWORD)

if __name__ == "__main__":
    main()
