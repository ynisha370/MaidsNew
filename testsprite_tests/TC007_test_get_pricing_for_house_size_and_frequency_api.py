import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_get_pricing_for_house_size_and_frequency_api():
    house_size = "medium"
    frequency = "weekly"
    url = f"{BASE_URL}/api/pricing/{house_size}/{frequency}"
    headers = {
        "Accept": "application/json",
    }
    try:
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
        assert response.status_code == 200, f"Expected status code 200 but got {response.status_code}"
        json_data = response.json()
        # Basic validation: response should be a dict/object containing pricing info
        assert isinstance(json_data, dict), "Response JSON is not a dictionary"
        # Check presence of expected keys that might appear in pricing info, e.g. price or similar
        # Since no specific schema given beyond dynamic pricing info, assert presence of at least one key
        assert len(json_data) > 0, "Pricing information is empty"
    except requests.exceptions.RequestException as e:
        assert False, f"Request failed: {e}"

test_get_pricing_for_house_size_and_frequency_api()