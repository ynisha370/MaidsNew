import requests
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_create_new_booking_api():
    # Step 1: Get list of services to obtain a valid service_id
    services_url = f"{BASE_URL}/api/services"
    try:
        services_response = requests.get(services_url, timeout=TIMEOUT)
        services_response.raise_for_status()
        services_data = services_response.json()
        assert isinstance(services_data, list) and len(services_data) > 0, "No services found"
        service_id = services_data[0].get("id") or services_data[0].get("_id") or services_data[0].get("service_id")
        assert service_id, "Service ID not found in service data"
    except (requests.RequestException, AssertionError) as e:
        raise Exception(f"Failed to get valid service_id for booking creation: {e}")

    # Prepare booking data
    customer_email = "testcustomer@example.com"
    customer_name = "Test Customer"
    date = (datetime.utcnow() + timedelta(days=2)).strftime("%Y-%m-%d")
    time = "10:00"

    booking_payload = {
        "service_id": service_id,
        "customer_email": customer_email,
        "customer_name": customer_name,
        "date": date,
        "time": time
    }

    booking_url = f"{BASE_URL}/api/bookings"
    headers = {
        "Content-Type": "application/json"
    }

    booking_id = None
    try:
        response = requests.post(booking_url, json=booking_payload, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        resp_json = response.json()
        # Expecting some identification of created booking in response; try to fetch booking id if present
        booking_id = resp_json.get("id") or resp_json.get("_id") or resp_json.get("booking_id")
    except (requests.RequestException, AssertionError) as e:
        raise AssertionError(f"Booking creation failed: {e}")
    finally:
        # Clean up: delete the booking if the API supports deletion (no info about delete in PRD)
        if booking_id:
            try:
                delete_url = f"{BASE_URL}/api/bookings/{booking_id}"
                del_resp = requests.delete(delete_url, timeout=TIMEOUT)
                # Accept 200 or 204 as success deletion status code if delete implemented
                if del_resp.status_code not in (200, 204):
                    pass  # No assertion on deletion, just clean up silently
            except requests.RequestException:
                pass

test_create_new_booking_api()