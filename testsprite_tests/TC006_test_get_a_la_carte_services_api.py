import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_get_a_la_carte_services_api():
    url = f"{BASE_URL}/api/services/a-la-carte"
    headers = {
        "Accept": "application/json"
    }
    try:
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request to {url} failed: {e}"
    
    assert response.status_code == 200, f"Expected status code 200 but got {response.status_code}"
    try:
        data = response.json()
    except ValueError:
        assert False, "Response is not valid JSON"
    
    assert isinstance(data, list), f"Expected response to be a list but got {type(data)}"
    
    # Optional: further validation of list content could be here if schema is known

test_get_a_la_carte_services_api()