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
    {"name": "Bruce Schneier", "phone_number": "(703)111-2121", "expected_status": 200, "description": "Acceptable input: Bruce Schneier"},
    {"name": "Schneier, Bruce", "phone_number": "(703)111-2121", "expected_status": 200, "description": "Acceptable input: Schneier, Bruce"},
    {"name": "Schneier, Bruce Wayne", "phone_number": "(703)111-2121", "expected_status": 200, "description": "Acceptable input: Schneier, Bruce Wayne"},
    {"name": "O’Malley, John F.", "phone_number": "(703)111-2121", "expected_status": 200, "description": "Acceptable input: O’Malley, John F."},
    {"name": "John O’Malley-Smith", "phone_number": "(703)111-2121", "expected_status": 200, "description": "Acceptable input: John O’Malley-Smith"},
    {"name": "Cher", "phone_number": "(703)111-2121", "expected_status": 200, "description": "Acceptable input: Cher"},
    {"name": "Ron O’’Henry", "phone_number": "(703)111-2121", "expected_status": 400, "description": "Unacceptable input: Ron O’’Henry"},
    {"name": "Ron O’Henry-Smith-Barnes", "phone_number": "(703)111-2121", "expected_status": 400, "description": "Unacceptable input: Ron O’Henry-Smith-Barnes"},
    {"name": "L33t Hacker", "phone_number": "(703)111-2121", "expected_status": 400, "description": "Unacceptable input: L33t Hacker"},
    {"name": "<Script>alert(\"XSS\")</Script>", "phone_number": "(703)111-2121", "expected_status": 400, "description": "Unacceptable input: <Script>alert(\"XSS\")</Script>"},
    {"name": "Brad Everett Samuel Smith", "phone_number": "(703)111-2121", "expected_status": 400, "description": "Unacceptable input: Brad Everett Samuel Smith"},
    {"name": "select * from users;", "phone_number": "(703)111-2121", "expected_status": 400, "description": "Unacceptable input: select * from users;"}
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

def run_test_case(name, phone_number, expected_status, description, token):
    conn = http.client.HTTPConnection(HOST, PORT)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    body = json.dumps({"name": name, "phone_number": phone_number})
    
    conn.request("POST", ADD_PERSON_ENDPOINT, body, headers)
    response = conn.getresponse()
    status_code = response.status
    response_data = response.read().decode()

    # Determine if the test passed based on the status code
    if status_code == expected_status:
        if expected_status == 200:
            result = json.loads(response_data)
            if "name" in result and "phone_number" in result:
                print(f"[PASS] {description} - Expected status {expected_status} and received {status_code}")
            else:
                print(f"[FAIL] {description} - Expected name and phone_number in response, but got: {result}")
        elif expected_status == 400:
            result = json.loads(response_data)
            if "detail" in result:
                print(f"[PASS] {description} - Expected status {expected_status} and received {status_code}")
            else:
                print(f"[FAIL] {description} - Expected error detail but got: {result}")
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
        run_test_case(case["name"], case["phone_number"], case["expected_status"], case["description"], token)

if __name__ == "__main__":
    main()
