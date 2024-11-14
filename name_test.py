import http.client
import json

# API host and endpoints
HOST = "127.0.0.1"
PORT = 8000
TOKEN_ENDPOINT = "/token"
ADD_PERSON_ENDPOINT = "/PhoneBook/add"

# User credentials for token retrieval
USERNAME = "writer"
PASSWORD = "password123"

# Define the test cases with the correct field names
test_cases = [
    {"name": "Bruce Schneier", "phone_number": "+111222", "expected_status": 200, "description": "Acceptable input: Bruce Schneier"},
    {"name": "Schneier, Bruce", "phone_number": "+111222", "expected_status": 200, "description": "Acceptable input: Schneier, Bruce"},
    {"name": "Schneier, Bruce Wayne", "phone_number": "+111222", "expected_status": 200, "description": "Acceptable input: Schneier, Bruce Wayne"},
    {"name": "O’Malley, John F.", "phone_number": "+111222", "expected_status": 200, "description": "Acceptable input: O’Malley, John F."},
    {"name": "John O’Malley-Smith", "phone_number": "+111222", "expected_status": 200, "description": "Acceptable input: John O’Malley-Smith"},
    {"name": "Cher", "phone_number": "+111222", "expected_status": 200, "description": "Acceptable input: Cher"},
    {"name": "Ron O’’Henry", "phone_number": "+111222", "expected_status": 400, "description": "Unacceptable input: Ron O’’Henry"},
    {"name": "Ron O’Henry-Smith-Barnes", "phone_number": "+111222", "expected_status": 400, "description": "Unacceptable input: Ron O’Henry-Smith-Barnes"},
    {"name": "L33t Hacker", "phone_number": "+111222", "expected_status": 400, "description": "Unacceptable input: L33t Hacker"},
    {"name": "<Script>alert(\"XSS\")</Script>", "phone_number": "+111222", "expected_status": 400, "description": "Unacceptable input: <Script>alert(\"XSS\")</Script>"},
    {"name": "Brad Everett Samuel Smith", "phone_number": "+111222", "expected_status": 400, "description": "Unacceptable input: Brad Everett Samuel Smith"},
    {"name": "select * from users;", "phone_number": "+111222", "expected_status": 400, "description": "Unacceptable input: select * from users;"}
]

# Function to get access token with debugging output
def get_access_token():
    conn = http.client.HTTPConnection(HOST, PORT)
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    body = f"username={USERNAME}&password={PASSWORD}"
    
    # Send POST request to /token endpoint
    conn.request("POST", TOKEN_ENDPOINT, body, headers)
    response = conn.getresponse()
    response_data = response.read().decode()
    
    # Check if the token request was successful
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

# Function to send a request to add a person and check the response status code
def run_test_case(name, phone_number, expected_status, description, token):
    conn = http.client.HTTPConnection(HOST, PORT)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    body = json.dumps({"name": name, "phone_number": phone_number})
    
    # Send POST request to /PhoneBook/add endpoint
    conn.request("POST", ADD_PERSON_ENDPOINT, body, headers)
    response = conn.getresponse()
    status_code = response.status
    response_data = response.read().decode()

    # Determine if the test passed based on the status code
    if status_code == expected_status:
        if expected_status == 200:
            # Parse response and check for name and phone_number fields
            result = json.loads(response_data)
            if "name" in result and "phone_number" in result:
                print(f"[PASS] {description} - Expected status {expected_status} and received {status_code}")
            else:
                print(f"[FAIL] {description} - Expected name and phone_number in response, but got: {result}")
        elif expected_status == 400:
            # Check for error detail in response body
            result = json.loads(response_data)
            if "detail" in result:
                print(f"[PASS] {description} - Expected status {expected_status} and received {status_code}")
            else:
                print(f"[FAIL] {description} - Expected error detail but got: {result}")
    else:
        # Debugging: Print the response details for unexpected status codes
        print(f"[FAIL] {description} - Expected status {expected_status} but received {status_code}")
        print(f"[DEBUG] Response Data: {response_data}")

    conn.close()

# Main function to execute the tests
def main():
    # Step 1: Get access token
    token = get_access_token()
    if not token:
        print("[ERROR] Cannot proceed with tests without an access token.")
        return
    
    # Step 2: Run each test case with the token
    for case in test_cases:
        run_test_case(case["name"], case["phone_number"], case["expected_status"], case["description"], token)

# Run the main function
if __name__ == "__main__":
    main()
