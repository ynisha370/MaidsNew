"""
Comprehensive Integration Test Suite for Cleaner-Admin Calendar System
Tests all endpoints and integrations (excluding payments)
"""

import requests
import json
from datetime import datetime, timedelta
import time

# Configuration
BASE_URL = "http://localhost:5000/api"
ADMIN_EMAIL = "admin@maids.com"
ADMIN_PASSWORD = "admin123"
CLEANER_EMAIL = "cleaner@maids.com"
CLEANER_PASSWORD = "cleaner123"
TEST_CUSTOMER_EMAIL = "test@maids.com"
TEST_CUSTOMER_PASSWORD = "test@maids@1234"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def add_result(self, test_name, passed, message=""):
        self.tests.append({"name": test_name, "passed": passed, "message": message})
        if passed:
            self.passed += 1
            print(f"{Colors.GREEN}[PASS]{Colors.END} {test_name}")
        else:
            self.failed += 1
            print(f"{Colors.RED}[FAIL]{Colors.END} {test_name}")
            if message:
                print(f"  {Colors.RED}{message}{Colors.END}")
    
    def print_summary(self):
        print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}Test Summary{Colors.END}")
        print(f"{'='*60}")
        print(f"Total Tests: {self.passed + self.failed}")
        print(f"{Colors.GREEN}Passed: {self.passed}{Colors.END}")
        print(f"{Colors.RED}Failed: {self.failed}{Colors.END}")
        print(f"{'='*60}\n")
        
        if self.failed > 0:
            print(f"{Colors.RED}Failed Tests:{Colors.END}")
            for test in self.tests:
                if not test["passed"]:
                    print(f"  - {test['name']}: {test['message']}")

results = TestResults()
admin_token = None
cleaner_token = None
customer_token = None
test_booking_id = None
test_cleaner_id = None

def test_admin_login():
    """Test admin authentication"""
    global admin_token
    print(f"\n{Colors.BLUE}{Colors.BOLD}Testing Admin Authentication{Colors.END}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        
        if response.status_code == 200:
            data = response.json()
            admin_token = data.get("access_token")
            results.add_result("Admin Login", admin_token is not None)
            return admin_token is not None
        else:
            results.add_result("Admin Login", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        results.add_result("Admin Login", False, str(e))
        return False

def test_cleaner_login():
    """Test cleaner authentication"""
    global cleaner_token, test_cleaner_id
    print(f"\n{Colors.BLUE}{Colors.BOLD}Testing Cleaner Authentication{Colors.END}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/cleaner/login",
            params={"email": CLEANER_EMAIL, "password": CLEANER_PASSWORD}
        )
        
        if response.status_code == 200:
            data = response.json()
            cleaner_token = data.get("token")
            test_cleaner_id = data.get("user", {}).get("id")
            results.add_result("Cleaner Login", cleaner_token is not None and test_cleaner_id is not None)
            return cleaner_token is not None
        else:
            results.add_result("Cleaner Login", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        results.add_result("Cleaner Login", False, str(e))
        return False

def test_customer_login():
    """Test customer authentication"""
    global customer_token
    print(f"\n{Colors.BLUE}{Colors.BOLD}Testing Customer Authentication{Colors.END}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": TEST_CUSTOMER_EMAIL, "password": TEST_CUSTOMER_PASSWORD}
        )
        
        if response.status_code == 200:
            data = response.json()
            customer_token = data.get("access_token")
            results.add_result("Customer Login", customer_token is not None)
            return customer_token is not None
        else:
            results.add_result("Customer Login", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        results.add_result("Customer Login", False, str(e))
        return False

def test_admin_get_bookings():
    """Test admin can retrieve all bookings"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}Testing Admin Booking Management{Colors.END}")
    
    try:
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/admin/bookings", headers=headers)
        
        if response.status_code == 200:
            bookings = response.json()
            results.add_result("Admin Get Bookings", True, f"Found {len(bookings)} bookings")
            return True
        else:
            results.add_result("Admin Get Bookings", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        results.add_result("Admin Get Bookings", False, str(e))
        return False

def test_admin_get_cleaners():
    """Test admin can retrieve all cleaners"""
    global test_cleaner_id
    
    try:
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/admin/cleaners", headers=headers)
        
        if response.status_code == 200:
            cleaners = response.json()
            results.add_result("Admin Get Cleaners", len(cleaners) > 0, f"Found {len(cleaners)} cleaners")
            if len(cleaners) > 0 and not test_cleaner_id:
                test_cleaner_id = cleaners[0].get("id")
            return True
        else:
            results.add_result("Admin Get Cleaners", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        results.add_result("Admin Get Cleaners", False, str(e))
        return False

def test_create_test_booking():
    """Create a test booking for assignment testing"""
    global test_booking_id
    print(f"\n{Colors.BLUE}{Colors.BOLD}Testing Booking Creation{Colors.END}")
    
    try:
        headers = {"Authorization": f"Bearer {customer_token}"}
        
        # Get tomorrow's date
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        booking_data = {
            "houseSize": "MEDIUM",
            "frequency": "WEEKLY",
            "services": [],
            "aLaCarteServices": [],
            "bookingDate": tomorrow,
            "timeSlot": "10:00-12:00",
            "address": {
                "street": "123 Test Street",
                "city": "Cypress",
                "state": "TX",
                "zip_code": "77433"
            },
            "specialInstructions": "Test booking for cleaner assignment"
        }
        
        response = requests.post(
            f"{BASE_URL}/bookings/no-payment",
            json=booking_data,
            headers=headers
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            test_booking_id = data.get("id") or data.get("booking", {}).get("id")
            results.add_result("Create Test Booking", test_booking_id is not None, f"Booking ID: {test_booking_id}")
            return test_booking_id is not None
        else:
            results.add_result("Create Test Booking", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        results.add_result("Create Test Booking", False, str(e))
        return False

def test_admin_assign_cleaner_to_booking():
    """Test admin can assign cleaner to booking"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}Testing Cleaner Assignment{Colors.END}")
    
    if not test_booking_id or not test_cleaner_id:
        results.add_result("Assign Cleaner to Booking", False, "Missing booking or cleaner ID")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        update_data = {
            "cleaner_id": test_cleaner_id,
            "status": "confirmed"
        }
        
        response = requests.patch(
            f"{BASE_URL}/admin/bookings/{test_booking_id}",
            json=update_data,
            headers=headers
        )
        
        if response.status_code == 200:
            results.add_result("Assign Cleaner to Booking", True)
            return True
        else:
            results.add_result("Assign Cleaner to Booking", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        results.add_result("Assign Cleaner to Booking", False, str(e))
        return False

def test_admin_get_unassigned_jobs():
    """Test admin can get unassigned jobs"""
    try:
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/admin/calendar/unassigned-jobs", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            unassigned_jobs = data.get("unassigned_jobs", [])
            results.add_result("Admin Get Unassigned Jobs", True, f"Found {len(unassigned_jobs)} unassigned jobs")
            return True
        else:
            results.add_result("Admin Get Unassigned Jobs", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        results.add_result("Admin Get Unassigned Jobs", False, str(e))
        return False

def test_cleaner_get_profile():
    """Test cleaner can get their profile"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}Testing Cleaner Profile Management{Colors.END}")
    
    try:
        headers = {"Authorization": f"Bearer {cleaner_token}"}
        response = requests.get(f"{BASE_URL}/cleaner/profile", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            user = data.get("user", {})
            results.add_result("Cleaner Get Profile", user.get("email") == CLEANER_EMAIL)
            return True
        else:
            results.add_result("Cleaner Get Profile", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        results.add_result("Cleaner Get Profile", False, str(e))
        return False

def test_cleaner_get_jobs():
    """Test cleaner can view their assigned jobs"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}Testing Cleaner Job Viewing{Colors.END}")
    
    try:
        headers = {"Authorization": f"Bearer {cleaner_token}"}
        response = requests.get(f"{BASE_URL}/cleaner/jobs", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            jobs = data.get("jobs", [])
            results.add_result("Cleaner Get Jobs", True, f"Found {len(jobs)} assigned jobs")
            return True
        else:
            results.add_result("Cleaner Get Jobs", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        results.add_result("Cleaner Get Jobs", False, str(e))
        return False

def test_cleaner_clock_in():
    """Test cleaner can clock in to a job"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}Testing Clock In/Out Functionality{Colors.END}")
    
    if not test_booking_id:
        results.add_result("Cleaner Clock In", False, "No test booking available")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {cleaner_token}"}
        clock_in_data = {
            "jobId": test_booking_id,
            "latitude": 29.9511,
            "longitude": -95.3698
        }
        
        response = requests.post(
            f"{BASE_URL}/cleaner/clock-in",
            json=clock_in_data,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            results.add_result("Cleaner Clock In", data.get("message") == "Clocked in successfully")
            return True
        else:
            results.add_result("Cleaner Clock In", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        results.add_result("Cleaner Clock In", False, str(e))
        return False

def test_cleaner_update_eta():
    """Test cleaner can update ETA"""
    if not test_booking_id:
        results.add_result("Cleaner Update ETA", False, "No test booking available")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {cleaner_token}"}
        eta_data = {
            "jobId": test_booking_id,
            "eta": "15 minutes"
        }
        
        response = requests.post(
            f"{BASE_URL}/cleaner/update-eta",
            json=eta_data,
            headers=headers
        )
        
        if response.status_code == 200:
            results.add_result("Cleaner Update ETA", True)
            return True
        else:
            results.add_result("Cleaner Update ETA", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        results.add_result("Cleaner Update ETA", False, str(e))
        return False

def test_cleaner_send_message():
    """Test cleaner can send message to client"""
    if not test_booking_id:
        results.add_result("Cleaner Send Message", False, "No test booking available")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {cleaner_token}"}
        message_data = {
            "jobId": test_booking_id,
            "message": "On my way! Will arrive in 15 minutes."
        }
        
        response = requests.post(
            f"{BASE_URL}/cleaner/send-message",
            json=message_data,
            headers=headers
        )
        
        if response.status_code == 200:
            results.add_result("Cleaner Send Message", True)
            return True
        else:
            results.add_result("Cleaner Send Message", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        results.add_result("Cleaner Send Message", False, str(e))
        return False

def test_cleaner_clock_out():
    """Test cleaner can clock out from a job"""
    if not test_booking_id:
        results.add_result("Cleaner Clock Out", False, "No test booking available")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {cleaner_token}"}
        clock_out_data = {
            "jobId": test_booking_id,
            "latitude": 29.9511,
            "longitude": -95.3698
        }
        
        response = requests.post(
            f"{BASE_URL}/cleaner/clock-out",
            json=clock_out_data,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            results.add_result("Cleaner Clock Out", data.get("message") == "Clocked out successfully")
            return True
        else:
            results.add_result("Cleaner Clock Out", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        results.add_result("Cleaner Clock Out", False, str(e))
        return False

def test_cleaner_earnings():
    """Test cleaner can view earnings"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}Testing Cleaner Wallet & Earnings{Colors.END}")
    
    try:
        headers = {"Authorization": f"Bearer {cleaner_token}"}
        response = requests.get(f"{BASE_URL}/cleaner/earnings", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            earnings = data.get("earnings", {})
            results.add_result("Cleaner Get Earnings", "totalEarnings" in earnings)
            return True
        else:
            results.add_result("Cleaner Get Earnings", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        results.add_result("Cleaner Get Earnings", False, str(e))
        return False

def test_cleaner_wallet():
    """Test cleaner can view wallet"""
    try:
        headers = {"Authorization": f"Bearer {cleaner_token}"}
        response = requests.get(f"{BASE_URL}/cleaner/wallet", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            wallet = data.get("wallet", {})
            results.add_result("Cleaner Get Wallet", "balance" in wallet)
            return True
        else:
            results.add_result("Cleaner Get Wallet", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        results.add_result("Cleaner Get Wallet", False, str(e))
        return False

def test_cleaner_payment_history():
    """Test cleaner can view payment history (excluding actual payment processing)"""
    try:
        headers = {"Authorization": f"Bearer {cleaner_token}"}
        response = requests.get(f"{BASE_URL}/cleaner/payments", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            payments = data.get("payments", [])
            results.add_result("Cleaner Payment History", True, f"Found {len(payments)} payment records")
            return True
        else:
            results.add_result("Cleaner Payment History", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        results.add_result("Cleaner Payment History", False, str(e))
        return False

def test_admin_calendar_availability():
    """Test admin can check calendar availability"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}Testing Admin Calendar Features{Colors.END}")
    
    try:
        headers = {"Authorization": f"Bearer {admin_token}"}
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        response = requests.get(
            f"{BASE_URL}/admin/calendar/availability-summary",
            params={"date": tomorrow},
            headers=headers
        )
        
        if response.status_code == 200:
            results.add_result("Admin Calendar Availability", True)
            return True
        else:
            results.add_result("Admin Calendar Availability", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        results.add_result("Admin Calendar Availability", False, str(e))
        return False

def test_admin_reports():
    """Test admin reporting functionality"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}Testing Admin Reports{Colors.END}")
    
    try:
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Test weekly report
        response = requests.get(f"{BASE_URL}/admin/reports/weekly", headers=headers)
        weekly_passed = response.status_code == 200
        results.add_result("Admin Weekly Report", weekly_passed)
        
        # Test monthly report
        response = requests.get(f"{BASE_URL}/admin/reports/monthly", headers=headers)
        monthly_passed = response.status_code == 200
        results.add_result("Admin Monthly Report", monthly_passed)
        
        return weekly_passed and monthly_passed
    except Exception as e:
        results.add_result("Admin Reports", False, str(e))
        return False

def test_booking_status_flow():
    """Test complete booking status flow"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}Testing Booking Status Flow{Colors.END}")
    
    if not test_booking_id:
        results.add_result("Booking Status Flow", False, "No test booking available")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{BASE_URL}/admin/bookings", headers=headers)
        
        if response.status_code == 200:
            bookings = response.json()
            test_booking = next((b for b in bookings if b.get("id") == test_booking_id), None)
            
            if test_booking:
                # Check if booking went through: pending -> confirmed -> in_progress -> completed
                final_status = test_booking.get("status")
                results.add_result("Booking Status Flow", final_status == "completed", 
                                 f"Final status: {final_status}")
                return True
            else:
                results.add_result("Booking Status Flow", False, "Test booking not found")
                return False
        else:
            results.add_result("Booking Status Flow", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        results.add_result("Booking Status Flow", False, str(e))
        return False

def run_all_tests():
    """Run all integration tests"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}Cleaner-Admin Calendar Integration Test Suite{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    print(f"{Colors.YELLOW}Testing against: {BASE_URL}{Colors.END}\n")
    
    # Authentication Tests
    if not test_admin_login():
        print(f"\n{Colors.RED}Admin login failed. Cannot continue.{Colors.END}")
        results.print_summary()
        return
    
    if not test_cleaner_login():
        print(f"\n{Colors.YELLOW}Warning: Cleaner login failed. Some tests will be skipped.{Colors.END}")
    
    if not test_customer_login():
        print(f"\n{Colors.YELLOW}Warning: Customer login failed. Some tests will be skipped.{Colors.END}")
    
    # Admin Tests
    test_admin_get_bookings()
    test_admin_get_cleaners()
    test_admin_get_unassigned_jobs()
    test_admin_calendar_availability()
    test_admin_reports()
    
    # Booking Creation and Assignment
    if customer_token:
        test_create_test_booking()
        time.sleep(1)  # Small delay to ensure booking is created
        test_admin_assign_cleaner_to_booking()
    
    # Cleaner Tests
    if cleaner_token:
        test_cleaner_get_profile()
        test_cleaner_get_jobs()
        
        if test_booking_id:
            test_cleaner_clock_in()
            time.sleep(1)
            test_cleaner_update_eta()
            test_cleaner_send_message()
            time.sleep(1)
            test_cleaner_clock_out()
            time.sleep(1)
            test_booking_status_flow()
        
        test_cleaner_earnings()
        test_cleaner_wallet()
        test_cleaner_payment_history()
    
    # Print results
    results.print_summary()
    
    # Save detailed results to file
    save_results_to_file()

def save_results_to_file():
    """Save test results to a JSON file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_results_cleaner_admin_{timestamp}.json"
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": results.passed + results.failed,
        "passed": results.passed,
        "failed": results.failed,
        "success_rate": f"{(results.passed / (results.passed + results.failed) * 100):.1f}%",
        "tests": results.tests
    }
    
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"{Colors.GREEN}Test results saved to: {filename}{Colors.END}")

if __name__ == "__main__":
    run_all_tests()

