import requests

BASE_URL = "http://localhost:8000"
STANDARD_SERVICES_ENDPOINT = "/api/services/standard"
TIMEOUT = 30

def test_get_standard_services_api():
    url = BASE_URL + STANDARD_SERVICES_ENDPOINT
    headers = {
        "Accept": "application/json"
    }
    try:
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        assert False, f"Request to get standard services failed: {e}"

    assert response.status_code == 200, f"Expected status code 200 but got {response.status_code}"

    try:
        services = response.json()
    except ValueError as e:
        assert False, f"Response is not valid JSON: {e}"

    assert isinstance(services, list), f"Expected response to be a list but got {type(services).__name__}"
    # Additional checks could be implemented here to verify schema if available

test_get_standard_services_api()
