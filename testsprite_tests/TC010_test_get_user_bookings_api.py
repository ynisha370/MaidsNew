import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

# Placeholder for a valid Bearer token for authentication
VALID_BEARER_TOKEN = "your_valid_bearer_token_here"

def test_get_user_bookings_api():
    url = f"{BASE_URL}/api/bookings"
    headers = {
        "Authorization": f"Bearer {VALID_BEARER_TOKEN}",
        "Accept": "application/json"
    }
    try:
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
        # Assert the status code is 200 OK
        assert response.status_code == 200, f"Expected status 200 but got {response.status_code}"
        data = response.json()
        # Assert the response JSON is a list (of bookings)
        assert isinstance(data, list), "Response JSON is not a list of bookings"
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"

test_get_user_bookings_api()