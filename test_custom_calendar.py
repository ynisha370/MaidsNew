"""
Comprehensive Test Suite for Custom Calendar System
Tests all calendar endpoints for customers, admin, and cleaners
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000/api"
ADMIN_EMAIL = "admin@maids.com"
ADMIN_PASSWORD = "admin123"

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
        print(f"{Colors.BOLD}Custom Calendar Test Summary{Colors.END}")
        print(f"{'='*60}")
        print(f"Total Tests: {self.passed + self.failed}")
        print(f"{Colors.GREEN}Passed: {self.passed}{Colors.END}")
        print(f"{Colors.RED}Failed: {self.failed}{Colors.END}")
        print(f"{'='*60}\n")

results = TestResults()
admin_token = None
test_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

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

def test_get_available_dates():
    """Test getting available dates for customer booking"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}Testing Customer Booking Calendar{Colors.END}")
    
    try:
        start_date = datetime.now().strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        response = requests.get(
            f"{BASE_URL}/calendar/available-dates",
            params={"start_date": start_date, "end_date": end_date}
        )
        
        if response.status_code == 200:
            data = response.json()
            available_dates = data.get("available_dates", [])
            results.add_result(
                "Get Available Dates", 
                isinstance(available_dates, list),
                f"Found {len(available_dates)} available dates"
            )
            return True
        else:
            results.add_result("Get Available Dates", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        results.add_result("Get Available Dates", False, str(e))
        return False

def test_get_time_slots_for_date():
    """Test getting time slots for a specific date"""
    try:
        response = requests.get(f"{BASE_URL}/calendar/time-slots/{test_date}")
        
        if response.status_code == 200:
            data = response.json()
            time_slots = data.get("time_slots", [])
            results.add_result(
                "Get Time Slots for Date",
                isinstance(time_slots, list),
                f"Found {len(time_slots)} time slots for {test_date}"
            )
            return True
        else:
            results.add_result("Get Time Slots for Date", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        results.add_result("Get Time Slots for Date", False, str(e))
        return False

def test_admin_calendar_overview():
    """Test admin calendar overview"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}Testing Admin Calendar Management{Colors.END}")
    
    if not admin_token:
        results.add_result("Admin Calendar Overview", False, "No admin token")
        return False
    
    try:
        start_date = datetime.now().strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(
            f"{BASE_URL}/admin/calendar/overview",
            params={"start_date": start_date, "end_date": end_date},
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            calendar_data = data.get("calendar_overview", [])
            results.add_result(
                "Admin Calendar Overview",
                isinstance(calendar_data, list),
                f"Retrieved {len(calendar_data)} days"
            )
            return True
        else:
            results.add_result("Admin Calendar Overview", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        results.add_result("Admin Calendar Overview", False, str(e))
        return False

def test_block_date():
    """Test admin blocking a date"""
    if not admin_token:
        results.add_result("Block Date", False, "No admin token")
        return False
    
    try:
        block_date = (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d")
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.post(
            f"{BASE_URL}/admin/calendar/block-date",
            json={
                "date": block_date,
                "time_slot": "10:00-12:00",
                "reason": "Test blocking"
            },
            headers=headers
        )
        
        if response.status_code == 200:
            results.add_result("Block Date", True, f"Blocked {block_date}")
            return True
        else:
            results.add_result("Block Date", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        results.add_result("Block Date", False, str(e))
        return False

def test_unblock_date():
    """Test admin unblocking a date"""
    if not admin_token:
        results.add_result("Unblock Date", False, "No admin token")
        return False
    
    try:
        block_date = (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d")
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.post(
            f"{BASE_URL}/admin/calendar/unblock-date",
            json={
                "date": block_date,
                "time_slot": "10:00-12:00"
            },
            headers=headers
        )
        
        if response.status_code == 200:
            results.add_result("Unblock Date", True)
            return True
        else:
            results.add_result("Unblock Date", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        results.add_result("Unblock Date", False, str(e))
        return False

def test_get_cleaner_availability():
    """Test getting cleaner availability"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}Testing Cleaner Availability{Colors.END}")
    
    if not admin_token:
        results.add_result("Get Cleaner Availability", False, "No admin token")
        return False
    
    try:
        # First get a cleaner ID
        headers = {"Authorization": f"Bearer {admin_token}"}
        cleaners_response = requests.get(f"{BASE_URL}/admin/cleaners", headers=headers)
        
        if cleaners_response.status_code != 200:
            results.add_result("Get Cleaner Availability", False, "Could not get cleaners list")
            return False
        
        cleaners = cleaners_response.json()
        if not cleaners:
            results.add_result("Get Cleaner Availability", False, "No cleaners available")
            return False
        
        cleaner_id = cleaners[0].get("id")
        start_date = datetime.now().strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        response = requests.get(
            f"{BASE_URL}/admin/calendar/cleaner-availability/{cleaner_id}",
            params={"start_date": start_date, "end_date": end_date},
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            availability = data.get("availability", [])
            results.add_result(
                "Get Cleaner Availability",
                isinstance(availability, list),
                f"Retrieved {len(availability)} days of availability"
            )
            return True
        else:
            results.add_result("Get Cleaner Availability", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        results.add_result("Get Cleaner Availability", False, str(e))
        return False

def test_get_calendar_events():
    """Test getting calendar events"""
    if not admin_token:
        results.add_result("Get Calendar Events", False, "No admin token")
        return False
    
    try:
        start_date = datetime.now().strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(
            f"{BASE_URL}/admin/calendar/events",
            params={"start_date": start_date, "end_date": end_date},
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            events = data.get("events", [])
            results.add_result(
                "Get Calendar Events",
                isinstance(events, list),
                f"Found {len(events)} calendar events"
            )
            return True
        else:
            results.add_result("Get Calendar Events", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        results.add_result("Get Calendar Events", False, str(e))
        return False

def test_calendar_integration_workflow():
    """Test complete calendar workflow"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}Testing Complete Calendar Workflow{Colors.END}")
    
    if not admin_token:
        results.add_result("Calendar Workflow", False, "No admin token")
        return False
    
    try:
        # Step 1: Check available dates (as customer)
        start_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        response = requests.get(
            f"{BASE_URL}/calendar/available-dates",
            params={"start_date": start_date, "end_date": end_date}
        )
        
        if response.status_code != 200:
            results.add_result("Calendar Workflow - Check Dates", False, "Could not get available dates")
            return False
        
        # Step 2: Get time slots for first available date
        available_dates = response.json().get("available_dates", [])
        if not available_dates:
            results.add_result("Calendar Workflow - Time Slots", False, "No available dates found")
            return False
        
        first_date = available_dates[0]["date"]
        slots_response = requests.get(f"{BASE_URL}/calendar/time-slots/{first_date}")
        
        if slots_response.status_code != 200:
            results.add_result("Calendar Workflow - Time Slots", False, "Could not get time slots")
            return False
        
        # Step 3: Admin blocks a future date
        future_date = (datetime.now() + timedelta(days=45)).strftime("%Y-%m-%d")
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        block_response = requests.post(
            f"{BASE_URL}/admin/calendar/block-date",
            json={"date": future_date, "reason": "Workflow test"},
            headers=headers
        )
        
        if block_response.status_code != 200:
            results.add_result("Calendar Workflow - Block Date", False, "Could not block date")
            return False
        
        # Step 4: Verify blocked date is not available
        verify_response = requests.get(f"{BASE_URL}/calendar/time-slots/{future_date}")
        
        if verify_response.status_code == 200:
            time_slots = verify_response.json().get("time_slots", [])
            all_blocked = all(slot.get("is_blocked", False) for slot in time_slots)
            
            if not all_blocked:
                results.add_result("Calendar Workflow - Verify Block", False, "Date not properly blocked")
                return False
        
        # Step 5: Unblock the date
        unblock_response = requests.post(
            f"{BASE_URL}/admin/calendar/unblock-date",
            json={"date": future_date},
            headers=headers
        )
        
        if unblock_response.status_code != 200:
            results.add_result("Calendar Workflow - Unblock", False, "Could not unblock date")
            return False
        
        results.add_result("Complete Calendar Workflow", True, "All workflow steps completed successfully")
        return True
        
    except Exception as e:
        results.add_result("Complete Calendar Workflow", False, str(e))
        return False

def test_time_slot_capacity():
    """Test time slot capacity management"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}Testing Capacity Management{Colors.END}")
    
    try:
        test_date_future = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
        response = requests.get(f"{BASE_URL}/calendar/time-slots/{test_date_future}")
        
        if response.status_code == 200:
            data = response.json()
            time_slots = data.get("time_slots", [])
            
            if time_slots:
                slot = time_slots[0]
                has_capacity = "total_capacity" in slot and "booked_count" in slot and "available_spots" in slot
                results.add_result(
                    "Time Slot Capacity Management",
                    has_capacity,
                    f"Capacity: {slot.get('total_capacity', 0)}, Booked: {slot.get('booked_count', 0)}, Available: {slot.get('available_spots', 0)}"
                )
                return has_capacity
            else:
                results.add_result("Time Slot Capacity Management", False, "No time slots found")
                return False
        else:
            results.add_result("Time Slot Capacity Management", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        results.add_result("Time Slot Capacity Management", False, str(e))
        return False

def run_all_tests():
    """Run all calendar tests"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}Custom Calendar System Test Suite{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    print(f"{Colors.YELLOW}Testing against: {BASE_URL}{Colors.END}\n")
    
    # Authentication
    if not test_admin_login():
        print(f"\n{Colors.RED}Admin login failed. Some tests will be skipped.{Colors.END}")
    
    # Customer booking calendar tests
    test_get_available_dates()
    test_get_time_slots_for_date()
    test_time_slot_capacity()
    
    # Admin calendar management tests
    test_admin_calendar_overview()
    test_block_date()
    test_unblock_date()
    test_get_calendar_events()
    
    # Cleaner availability tests
    test_get_cleaner_availability()
    
    # Integration workflow test
    test_calendar_integration_workflow()
    
    # Print results
    results.print_summary()
    
    # Save results
    save_results_to_file()

def save_results_to_file():
    """Save test results to a JSON file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_results_calendar_{timestamp}.json"
    
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

