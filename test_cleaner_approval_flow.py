"""
Comprehensive Test Suite for Cleaner Approval and Auto-Assignment System
Tests the complete flow from registration to booking assignment
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000/api"
ADMIN_EMAIL = "admin@maids.com"
ADMIN_PASSWORD = "admin123"

# Test data
TEST_CLEANER = {
    "name": "Test Cleaner Auto",
    "email": f"testcleaner{datetime.now().timestamp()}@test.com",
    "phone": "+1234567890",
    "password": "password123"
}

TEST_CUSTOMER_EMAIL = "testcustomer@test.com"
TEST_CUSTOMER_PASSWORD = "password123"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def log_test(test_name):
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}Testing: {test_name}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")

def log_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def log_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def log_info(message):
    print(f"{Colors.YELLOW}→ {message}{Colors.END}")

# Test 1: Cleaner Registration (Should be pending)
def test_cleaner_registration():
    log_test("Cleaner Registration with Pending Status")
    
    try:
        response = requests.post(
            f"{BASE_URL}/cleaner/register",
            data=TEST_CLEANER,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and not data.get("user", {}).get("isApproved", True):
                log_success("Cleaner registered successfully with pending status")
                log_info(f"Cleaner ID: {data['user']['id']}")
                log_info(f"Message: {data['message']}")
                return data['user']['id']
            else:
                log_error("Cleaner was not set to pending approval")
                return None
        else:
            log_error(f"Registration failed: {response.text}")
            return None
    except Exception as e:
        log_error(f"Exception: {str(e)}")
        return None

# Test 2: Unapproved Cleaner Login (Should be rejected)
def test_unapproved_login():
    log_test("Unapproved Cleaner Login Attempt (Should Fail)")
    
    try:
        response = requests.post(
            f"{BASE_URL}/cleaner/login",
            data={
                "email": TEST_CLEANER["email"],
                "password": TEST_CLEANER["password"]
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 403:
            log_success("Login correctly rejected for unapproved cleaner")
            log_info(f"Error message: {response.json().get('detail')}")
            return True
        else:
            log_error(f"Unexpected response: {response.status_code}")
            return False
    except Exception as e:
        log_error(f"Exception: {str(e)}")
        return False

# Test 3: Admin Login
def test_admin_login():
    log_test("Admin Login")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("token")
            log_success("Admin logged in successfully")
            log_info(f"Token: {token[:20]}...")
            return token
        else:
            log_error(f"Admin login failed: {response.text}")
            return None
    except Exception as e:
        log_error(f"Exception: {str(e)}")
        return None

# Test 4: Get Pending Cleaners
def test_get_pending_cleaners(admin_token):
    log_test("Get Pending Cleaners")
    
    try:
        response = requests.get(
            f"{BASE_URL}/admin/cleaners/pending",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            pending_cleaners = data.get("pending_cleaners", [])
            log_success(f"Found {len(pending_cleaners)} pending cleaners")
            
            # Find our test cleaner
            test_cleaner = next(
                (c for c in pending_cleaners if c["email"] == TEST_CLEANER["email"]),
                None
            )
            
            if test_cleaner:
                log_success(f"Test cleaner found in pending list: {test_cleaner['first_name']} {test_cleaner['last_name']}")
                return test_cleaner["id"]
            else:
                log_error("Test cleaner not found in pending list")
                return None
        else:
            log_error(f"Failed to get pending cleaners: {response.text}")
            return None
    except Exception as e:
        log_error(f"Exception: {str(e)}")
        return None

# Test 5: Approve Cleaner
def test_approve_cleaner(admin_token, cleaner_id):
    log_test("Approve Cleaner")
    
    try:
        response = requests.post(
            f"{BASE_URL}/admin/cleaners/{cleaner_id}/approve",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            log_success(data.get("message", "Cleaner approved"))
            return True
        else:
            log_error(f"Failed to approve cleaner: {response.text}")
            return False
    except Exception as e:
        log_error(f"Exception: {str(e)}")
        return False

# Test 6: Approved Cleaner Login (Should succeed)
def test_approved_login():
    log_test("Approved Cleaner Login (Should Succeed)")
    
    try:
        response = requests.post(
            f"{BASE_URL}/cleaner/login",
            data={
                "email": TEST_CLEANER["email"],
                "password": TEST_CLEANER["password"]
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            data = response.json()
            log_success("Approved cleaner logged in successfully")
            log_info(f"Cleaner: {data['user']['name']}")
            return data.get("token")
        else:
            log_error(f"Login failed: {response.text}")
            return None
    except Exception as e:
        log_error(f"Exception: {str(e)}")
        return None

# Test 7: Create Test Booking (Auto-assignment test)
def test_create_booking_with_auto_assignment():
    log_test("Create Booking with Auto-Assignment")
    
    # Future date
    booking_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    
    booking_data = {
        "house_size": "2_bedroom",
        "frequency": "one_time",
        "services": [
            {
                "service_id": "standard_cleaning",
                "service_name": "Standard Cleaning",
                "price": 150.0
            }
        ],
        "a_la_carte_services": [],
        "booking_date": booking_date,
        "time_slot": "10:00-12:00",
        "base_price": 150.0,
        "customer": {
            "email": TEST_CUSTOMER_EMAIL,
            "first_name": "Test",
            "last_name": "Customer",
            "phone": "+1234567890",
            "address": "123 Test St",
            "city": "Cypress",
            "state": "TX",
            "zip_code": "77433"
        },
        "address": {
            "street": "123 Test St",
            "city": "Cypress",
            "state": "TX",
            "zip_code": "77433"
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/bookings/guest",
            json=booking_data
        )
        
        if response.status_code == 200:
            data = response.json()
            booking_id = data.get("id")
            cleaner_id = data.get("cleaner_id")
            
            if cleaner_id:
                log_success(f"Booking created with auto-assigned cleaner!")
                log_info(f"Booking ID: {booking_id}")
                log_info(f"Assigned Cleaner ID: {cleaner_id}")
                log_info(f"Status: {data.get('status')}")
                return booking_id, cleaner_id
            else:
                log_success("Booking created but no cleaner available for auto-assignment")
                log_info(f"Booking ID: {booking_id}")
                return booking_id, None
        else:
            log_error(f"Booking creation failed: {response.text}")
            return None, None
    except Exception as e:
        log_error(f"Exception: {str(e)}")
        return None, None

# Test 8: Manual Reassignment (Should send notifications)
def test_manual_reassignment(admin_token, booking_id, new_cleaner_id):
    log_test("Manual Cleaner Reassignment (Notification Test)")
    
    try:
        response = requests.patch(
            f"{BASE_URL}/admin/bookings/{booking_id}",
            json={"cleaner_id": new_cleaner_id},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        if response.status_code == 200:
            log_success("Booking reassigned successfully")
            log_info("Notifications should be sent to old cleaner, new cleaner, and customer")
            return True
        else:
            log_error(f"Reassignment failed: {response.text}")
            return False
    except Exception as e:
        log_error(f"Exception: {str(e)}")
        return False

# Main test runner
def run_all_tests():
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}CLEANER APPROVAL & AUTO-ASSIGNMENT TEST SUITE{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    
    results = []
    
    # Test 1: Register cleaner
    cleaner_id = test_cleaner_registration()
    results.append(("Cleaner Registration", cleaner_id is not None))
    
    if not cleaner_id:
        log_error("Cannot continue tests without cleaner ID")
        return
    
    # Test 2: Try to login as unapproved cleaner
    results.append(("Unapproved Login Block", test_unapproved_login()))
    
    # Test 3: Admin login
    admin_token = test_admin_login()
    results.append(("Admin Login", admin_token is not None))
    
    if not admin_token:
        log_error("Cannot continue tests without admin token")
        return
    
    # Test 4: Get pending cleaners
    pending_cleaner_id = test_get_pending_cleaners(admin_token)
    results.append(("Get Pending Cleaners", pending_cleaner_id is not None))
    
    # Test 5: Approve cleaner
    if pending_cleaner_id:
        results.append(("Approve Cleaner", test_approve_cleaner(admin_token, pending_cleaner_id)))
    
    # Test 6: Login as approved cleaner
    cleaner_token = test_approved_login()
    results.append(("Approved Cleaner Login", cleaner_token is not None))
    
    # Test 7: Create booking with auto-assignment
    booking_id, assigned_cleaner_id = test_create_booking_with_auto_assignment()
    results.append(("Auto-Assignment on Booking", assigned_cleaner_id is not None))
    
    # Summary
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}TEST SUMMARY{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{Colors.GREEN}PASSED{Colors.END}" if result else f"{Colors.RED}FAILED{Colors.END}"
        print(f"{test_name}: {status}")
    
    print(f"\n{Colors.BLUE}Total: {passed}/{total} tests passed{Colors.END}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{'='*60}{Colors.END}")
        print(f"{Colors.GREEN}ALL TESTS PASSED! ✓{Colors.END}")
        print(f"{Colors.GREEN}{'='*60}{Colors.END}\n")
    else:
        print(f"\n{Colors.RED}{'='*60}{Colors.END}")
        print(f"{Colors.RED}SOME TESTS FAILED{Colors.END}")
        print(f"{Colors.RED}{'='*60}{Colors.END}\n")

if __name__ == "__main__":
    run_all_tests()

