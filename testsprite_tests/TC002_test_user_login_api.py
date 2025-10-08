import requests

def test_user_login_api():
    base_url = "http://localhost:8000"
    login_endpoint = f"{base_url}/api/auth/login"
    headers = {
        "Content-Type": "application/json"
    }
    # Example valid credentials for testing
    payload = {
        "email": "testuser@example.com",
        "password": "TestPassword123!"
    }

    try:
        response = requests.post(login_endpoint, json=payload, headers=headers, timeout=30)
    except requests.RequestException as e:
        assert False, f"Request to login endpoint failed: {e}"

    assert response.status_code == 200, f"Expected status code 200 but got {response.status_code}"
    # Optionally check response content for authentication token or success message
    try:
        json_response = response.json()
    except ValueError:
        assert False, "Response is not a valid JSON"

    # Basic validation: presence of token or similar field expected in login response
    assert "token" in json_response or "access_token" in json_response or "user" in json_response, \
        "Login response does not contain expected authentication information"

test_user_login_api()
