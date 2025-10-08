import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

# Provide a valid user email and password registered in the system for testing login
TEST_USER_EMAIL = "testuser@example.com"
TEST_USER_PASSWORD = "TestUserPassword123!"

def test_get_current_user_info_api():
    login_url = f"{BASE_URL}/api/auth/login"
    me_url = f"{BASE_URL}/api/auth/me"

    try:
        # Login to get Bearer token
        login_payload = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        login_resp = requests.post(login_url, json=login_payload, timeout=TIMEOUT)
        assert login_resp.status_code == 200, f"Login failed with status code {login_resp.status_code}"
        login_data = login_resp.json()
        token = login_data.get("access_token") or login_data.get("token") or login_data.get("accessToken")
        assert token, "Bearer token not found in login response"

        headers = {
            "Authorization": f"Bearer {token}"
        }

        # Request current user info
        me_resp = requests.get(me_url, headers=headers, timeout=TIMEOUT)
        assert me_resp.status_code == 200, f"/api/auth/me returned status code {me_resp.status_code}"
        user_info = me_resp.json()
        assert isinstance(user_info, dict), "User info response is not a JSON object"
        # Basic checks on expected keys that a user info should contain
        assert "email" in user_info, "User info does not contain 'email'"
        assert user_info["email"] == TEST_USER_EMAIL, "Returned user email does not match logged in user"
    except requests.RequestException as e:
        assert False, f"HTTP request failed: {e}"

test_get_current_user_info_api()
