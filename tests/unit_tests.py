import http.client
import json
import uuid
from urllib.parse import urlencode


HOST = "127.0.0.1"
PORT = 8000
USER_CREATION_ENDPOINT = "/users/"
TOKEN_ENDPOINT = "/token"
ADD_PERSON_ENDPOINT = "/PhoneBook/add"
LIST_PHONEBOOK_ENDPOINT = "/PhoneBook/list"
DELETE_BY_NAME_ENDPOINT = "/PhoneBook/deleteByName"
DELETE_BY_NUMBER_ENDPOINT = "/PhoneBook/deleteByNumber"


READ_USER = f"read_user_{uuid.uuid4().hex[:6]}"
READ_WRITE_USER = f"rw_user_{uuid.uuid4().hex[:6]}"
PASSWORD = "password123"


def create_user(username, password, role):
    conn = http.client.HTTPConnection(HOST, PORT)
    headers = {"Content-Type": "application/json"}
    body = json.dumps({"username": username, "password": password, "role": role})

    try:
        conn.request("POST", USER_CREATION_ENDPOINT, body, headers)
        response = conn.getresponse()
        status_code = response.status
        response_data = response.read().decode()

        if status_code == 200:
            print(f"[PASS] User '{username}' with role '{role}' created successfully.")
        else:
            print(f"[FAIL] Failed to create user '{username}' with role '{role}'.")
            print(f"[DEBUG] Response: {response_data}")
    except Exception as e:
        print(f"[ERROR] Exception during user creation: {e}")
    finally:
        conn.close()


def get_access_token(username, password):
    conn = http.client.HTTPConnection(HOST, PORT)
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    body = f"username={username}&password={password}"

    try:
        conn.request("POST", TOKEN_ENDPOINT, body, headers)
        response = conn.getresponse()
        response_data = response.read().decode()

        if response.status == 200:
            token_data = json.loads(response_data)
            access_token = token_data.get("access_token")
            print(f"[INFO] Access token for '{username}' retrieved successfully.")
            return access_token
        else:
            print(f"[ERROR] Failed to get access token for '{username}': {response.status}")
            print(f"[DEBUG] Response Data: {response_data}")
            return None
    except Exception as e:
        print(f"[ERROR] Exception while getting access token: {e}")
        return None
    finally:
        conn.close()


def list_phonebook(token):
    conn = http.client.HTTPConnection(HOST, PORT)
    headers = {"Authorization": f"Bearer {token}"}

    try:
        conn.request("GET", LIST_PHONEBOOK_ENDPOINT, headers=headers)
        response = conn.getresponse()
        status_code = response.status
        response_data = response.read().decode()

        if status_code == 200:
            print(f"[PASS] Phonebook list retrieved successfully.")
            print(f"[INFO] Phonebook Entries: {response_data}")
        else:
            print(f"[FAIL] Failed to list phonebook. Status code: {status_code}")
            print(f"[DEBUG] Response Data: {response_data}")
    except Exception as e:
        print(f"[ERROR] Exception during phonebook listing: {e}")
    finally:
        conn.close()


def add_phonebook_entry(name, phone_number, token):
    conn = http.client.HTTPConnection(HOST, PORT)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    body = json.dumps({"name": name, "phone_number": phone_number})

    try:
        conn.request("POST", ADD_PERSON_ENDPOINT, body, headers)
        response = conn.getresponse()
        status_code = response.status
        response_data = response.read().decode()

        if status_code == 200:
            print(f"[PASS] Added phonebook entry: {name}, {phone_number}")
        else:
            print(f"[FAIL] Failed to add phonebook entry: {name}, {phone_number}. Status code: {status_code}")
            print(f"[DEBUG] Response Data: {response_data}")
    except Exception as e:
        print(f"[ERROR] Exception during adding phonebook entry: {e}")
    finally:
        conn.close()


def delete_by_name(name, token):
    conn = http.client.HTTPConnection(HOST, PORT)
    headers = {"Authorization": f"Bearer {token}"}
    params = urlencode({"name": name})  

    try:
        conn.request("PUT", f"{DELETE_BY_NAME_ENDPOINT}?{params}", headers=headers)
        response = conn.getresponse()
        status_code = response.status
        response_data = response.read().decode()

        if status_code == 200:
            print(f"[PASS] Deleted phonebook entry by name: {name}")
        else:
            print(f"[FAIL] Failed to delete entry by name: {name}. Status code: {status_code}")
            print(f"[DEBUG] Response Data: {response_data}")
    except Exception as e:
        print(f"[ERROR] Exception during deleting by name: {e}")
    finally:
        conn.close()





def main():
    create_user(READ_USER, PASSWORD, "Read")
    create_user(READ_WRITE_USER, PASSWORD, "Read/Write")

    read_token = get_access_token(READ_USER, PASSWORD)
    rw_token = get_access_token(READ_WRITE_USER, PASSWORD)

    if not read_token or not rw_token:
        print("[ERROR] Cannot proceed without valid tokens.")
        return

    print("\n[INFO] Testing Read-Only User:")
    list_phonebook(read_token)

    print("\n[INFO] Testing Read/Write User:")
    add_phonebook_entry("Test User", "(703)111-2121", rw_token)
    list_phonebook(rw_token)
    delete_by_name("Test User", rw_token)



if __name__ == "__main__":
    main()
