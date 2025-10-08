import requests
import uuid

BASE_URL = "http://localhost:8000"
REGISTER_ENDPOINT = "/api/auth/register"
TIMEOUT = 30

def test_user_registration_api():
    url = BASE_URL + REGISTER_ENDPOINT
    unique_email = f"testuser_{uuid.uuid4()}@example.com"
    payload = {
        "email": unique_email,
        "password": "StrongPassw0rd!",
        "first_name": "Test",
        "last_name": "User"
    }
    headers = {
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request to register user failed: {e}"

    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    # Optionally check response content if API returns any (not specified)

test_user_registration_api()