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

# Function to get access token with debugging output
def get_access_token():
    conn = http.client.HTTPConnection(HOST, PORT)
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    body = f"username={USERNAME}&password={PASSWORD}"
    
    try:
        # Send POST request to /token endpoint
        conn.request("POST", TOKEN_ENDPOINT, body, headers)
        response = conn.getresponse()
        response_data = response.read().decode()
        
        # Check if the token request was successful
        if response.status == 200:
            token_data = json.loads(response_data)
            access_token = token_data.get("access_token")
            print("[INFO] Access token retrieved successfully.")
            return access_token
        else:
            print(f"[ERROR] Failed to get access token: {response.status}")
            print(f"[DEBUG] Response Data: {response_data}")
            return None
    except Exception as e:
        print(f"[ERROR] Exception occurred while getting access token: {e}")
        return None
    finally:
        conn.close()

# Function to send a request to add a person and check the response status code
def run_test_case(phone_number, expected_status, description, token):
    conn = http.client.HTTPConnection(HOST, PORT)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    # Using a fixed valid name for phone number testing
    body = json.dumps({"name": "Test User", "phone_number": phone_number})
    
    try:
        # Send POST request to /PhoneBook/add endpoint
        conn.request("POST", ADD_PERSON_ENDPOINT, body, headers)
        response = conn.getresponse()
        status_code = response.status
        response_data = response.read().decode()

        # Determine if the test passed based on the status code
        if status_code == expected_status:
            if expected_status == 200:
                # Parse response and check for name and phone_number fields
                try:
                    result = json.loads(response_data)
                    if "name" in result and "phone_number" in result:
                        print(f"[PASS] {description} - Expected status {expected_status} and received {status_code}")
                    else:
                        print(f"[FAIL] {description} - Expected name and phone_number in response, but got: {result}")
                except json.JSONDecodeError:
                    print(f"[FAIL] {description} - Expected JSON response, but received: {response_data}")
            elif expected_status == 400:
                # Check for error detail in response body
                try:
                    result = json.loads(response_data)
                    if "detail" in result:
                        print(f"[PASS] {description} - Expected status {expected_status} and received {status_code}")
                    else:
                        print(f"[FAIL] {description} - Expected error detail but got: {result}")
                except json.JSONDecodeError:
                    print(f"[FAIL] {description} - Expected JSON response, but received: {response_data}")
        else:
            # Debugging: Print the response details for unexpected status codes
            print(f"[FAIL] {description} - Expected status {expected_status} but received {status_code}")
            print(f"[DEBUG] Response Data: {response_data}")
    except Exception as e:
        print(f"[FAIL] {description} - Exception occurred: {e}")
    finally:
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
        run_test_case(
            phone_number=case["phone_number"],
            expected_status=case["expected_status"],
            description=case["description"],
            token=token
        )

# Run the main function
if __name__ == "__main__":
    main()
