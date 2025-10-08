import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_get_room_pricing_information_api():
    url = f"{BASE_URL}/api/room-pricing"
    headers = {
        "Accept": "application/json"
    }
    try:
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
        assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
        data = response.json()
        # Validate that the response contains pricing details (basic structure check)
        assert isinstance(data, dict), "Response JSON should be an object"
        assert len(data) > 0, "Response JSON should not be empty"
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"

test_get_room_pricing_information_api()