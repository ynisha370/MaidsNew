import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_get_all_services_api():
    url = f"{BASE_URL}/api/services"
    headers = {
        "Accept": "application/json"
    }
    try:
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, list), "Response is not a list"
        # Basic check: each item should at least have an identifier or name (loosely checking keys)
        for service in data:
            assert isinstance(service, dict), "Service item is not a dictionary"
            # We expect both standard and a-la-carte, so maybe check keys presence loosely
            assert 'id' in service or 'name' in service or 'type' in service, "Service item missing expected keys"
    except requests.exceptions.RequestException as e:
        assert False, f"Request failed: {e}"

test_get_all_services_api()