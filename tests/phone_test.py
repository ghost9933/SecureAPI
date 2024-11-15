import http.client
import json

HOST = "127.0.0.1"
PORT = 8000
USER_CREATION_ENDPOINT = "/users/"
TOKEN_ENDPOINT = "/token"
ADD_PERSON_ENDPOINT = "/PhoneBook/add"

USERNAME = "test_writer"
PASSWORD = "password123"
ROLE = "Read/Write"

test_cases = [
    # Acceptable inputs
    {"phone_number": "12345", "expected_status": 200, "description": "Acceptable input: 12345"},
    {"phone_number": "(703)111-2121", "expected_status": 200, "description": "Acceptable input: (703)111-2121"},
    {"phone_number": "123-1234", "expected_status": 200, "description": "Acceptable input: 123-1234"},
    {"phone_number": "+1(703)111-2121", "expected_status": 200, "description": "Acceptable input: +1(703)111-2121"},
    {"phone_number": "+32 (21) 212-2324", "expected_status": 200, "description": "Acceptable input: +32 (21) 212-2324"},
    {"phone_number": "1(703)123-1234", "expected_status": 200, "description": "Acceptable input: 1(703)123-1234"},
    {"phone_number": "011 701 111 1234", "expected_status": 200, "description": "Acceptable input: 011 701 111 1234"},
    {"phone_number": "12345.12345", "expected_status": 200, "description": "Acceptable input: 12345.12345"},
    {"phone_number": "011 1 703 111 1234", "expected_status": 200, "description": "Acceptable input: 011 1 703 111 1234"},
    
    # Unacceptable inputs
    {"phone_number": "123", "expected_status": 400, "description": "Unacceptable input: 123"},
    {"phone_number": "1/703/123/1234", "expected_status": 400, "description": "Unacceptable input: 1/703/123/1234"},
    {"phone_number": "Nr 102-123-1234", "expected_status": 400, "description": "Unacceptable input: Nr 102-123-1234"},
    {"phone_number": "<script>alert(\"XSS\")</script>", "expected_status": 400, "description": "Unacceptable input: <Script>alert(\"XSS\")</Script>"},
    {"phone_number": "7031111234", "expected_status": 400, "description": "Unacceptable input: 7031111234"},
    {"phone_number": "+1234 (201) 123-1234", "expected_status": 400, "description": "Unacceptable input: +1234 (201) 123-1234"},
    {"phone_number": "(001) 123-1234", "expected_status": 400, "description": "Unacceptable input: (001) 123-1234"},
    {"phone_number": "+01 (703) 123-1234", "expected_status": 400, "description": "Unacceptable input: +01 (703) 123-1234"},
    {"phone_number": "(703) 123-1234 ext 204", "expected_status": 400, "description": "Unacceptable input: (703) 123-1234 ext 204"},
]

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
        print("[INFO] Access token retrieved successfully.")
        conn.close()
        return access_token
    else:
        print(f"[ERROR] Failed to get access token: {response.status}")
        conn.close()
        return None

def run_test_case(phone_number, expected_status, description, token):
    conn = http.client.HTTPConnection(HOST, PORT)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    body = json.dumps({"name": "Test User", "phone_number": phone_number})
    
    conn.request("POST", ADD_PERSON_ENDPOINT, body, headers)
    response = conn.getresponse()
    status_code = response.status
    response_data = response.read().decode()

    if status_code == expected_status:
        print(f"[PASS] {description} - Expected status {expected_status} and received {status_code}")
    else:
        print(f"[FAIL] {description} - Expected status {expected_status} but received {status_code}")
        print(f"[DEBUG] Response Data: {response_data}")

    conn.close()

def main():
    create_user(USERNAME, PASSWORD, ROLE)
    
    token = get_access_token(USERNAME, PASSWORD)
    if not token:
        print("[ERROR] Cannot proceed with tests without an access token.")
        return
    
    for case in test_cases:
        run_test_case(
            phone_number=case["phone_number"],
            expected_status=case["expected_status"],
            description=case["description"],
            token=token
        )

if __name__ == "__main__":
    main()
