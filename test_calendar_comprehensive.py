#!/usr/bin/env python3
"""
Comprehensive Calendar Job Assignment Testing
Tests the calendar drag-and-drop functionality and cleaner calendar integration
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000/api"
ADMIN_EMAIL = "admin@maids.com"
ADMIN_PASSWORD = "admin123"

class CalendarTester:
    def __init__(self):
        self.admin_token = None
        self.test_results = []
        
    def log_result(self, test_name, status, details=""):
        result = {
            "test": test_name,
            "status": "✅ PASS" if status else "❌ FAIL",
            "details": details
        }
        self.test_results.append(result)
        print(f"{result['status']} - {test_name}")
        if details:
            print(f"   {details}")
    
    def admin_login(self):
        """Login as admin to get authentication token"""
        print("\n=== Admin Login ===")
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
            )
            if response.status_code == 200:
                self.admin_token = response.json().get("access_token")
                self.log_result("Admin Login", True, f"Token obtained")
                return True
            else:
                self.log_result("Admin Login", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Admin Login", False, str(e))
            return False
    
    def test_get_unassigned_jobs(self):
        """Test GET /api/admin/calendar/unassigned-jobs"""
        print("\n=== Test Get Unassigned Jobs ===")
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{BASE_URL}/admin/calendar/unassigned-jobs", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                unassigned_jobs = data.get("unassigned_jobs", [])
                self.log_result("Get Unassigned Jobs", True, 
                    f"Found {len(unassigned_jobs)} unassigned jobs")
                
                # Display first few jobs
                for job in unassigned_jobs[:3]:
                    print(f"   Job {job['id'][:8]}: {job.get('house_size')} on {job.get('booking_date')}")
                    print(f"      Time: {job.get('time_slot')}, Amount: ${job.get('total_amount')}")
                    print(f"      Has cleaner_id: {'cleaner_id' in job}")
                
                return True, unassigned_jobs
            else:
                self.log_result("Get Unassigned Jobs", False, 
                    f"Status: {response.status_code}, {response.text}")
                return False, []
        except Exception as e:
            self.log_result("Get Unassigned Jobs", False, str(e))
            return False, []
    
    def test_get_availability_summary(self, test_date=None):
        """Test GET /api/admin/calendar/availability-summary"""
        print("\n=== Test Get Availability Summary ===")
        if not test_date:
            test_date = datetime.now().strftime("%Y-%m-%d")
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(
                f"{BASE_URL}/admin/calendar/availability-summary?date={test_date}",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                cleaners = data.get("cleaners", [])
                time_slots = data.get("time_slots", [])
                
                self.log_result("Get Availability Summary", True,
                    f"Found {len(cleaners)} cleaners, {len(time_slots)} time slots")
                
                # Analyze cleaner data
                for cleaner in cleaners[:3]:
                    print(f"\n   Cleaner: {cleaner.get('cleaner_name')}")
                    print(f"      ID: {cleaner.get('cleaner_id')}")
                    print(f"      Calendar Enabled: {cleaner.get('calendar_enabled')}")
                    
                    # Check slots
                    slots = cleaner.get('slots', {})
                    print(f"      Slots defined: {list(slots.keys())}")
                    
                    # Check for existing jobs
                    total_existing_jobs = 0
                    for slot_name, slot_data in slots.items():
                        existing_jobs = slot_data.get('existing_jobs', [])
                        if existing_jobs:
                            print(f"         {slot_name}: {len(existing_jobs)} jobs assigned")
                            for job in existing_jobs:
                                print(f"            - Booking {job.get('id', 'N/A')[:8]}: Status={job.get('status')}")
                            total_existing_jobs += len(existing_jobs)
                        else:
                            print(f"         {slot_name}: Available={slot_data.get('available')}, No jobs")
                    
                    if total_existing_jobs == 0:
                        print(f"      ⚠️  No jobs assigned to this cleaner")
                
                return True, data
            else:
                self.log_result("Get Availability Summary", False,
                    f"Status: {response.status_code}, {response.text}")
                return False, None
        except Exception as e:
            self.log_result("Get Availability Summary", False, str(e))
            return False, None
    
    def test_get_all_cleaners(self):
        """Test GET /api/admin/cleaners"""
        print("\n=== Test Get All Cleaners ===")
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{BASE_URL}/admin/cleaners", headers=headers)
            
            if response.status_code == 200:
                cleaners = response.json()
                self.log_result("Get All Cleaners", True, f"Found {len(cleaners)} cleaners")
                
                # Check cleaner fields
                for cleaner in cleaners[:5]:
                    print(f"\n   Cleaner: {cleaner.get('first_name')} {cleaner.get('last_name')}")
                    print(f"      Email: {cleaner.get('email')}")
                    print(f"      Active: {cleaner.get('is_active')}")
                    print(f"      Has first_name: {bool(cleaner.get('first_name'))}")
                    print(f"      Has last_name: {bool(cleaner.get('last_name'))}")
                    print(f"      Calendar enabled: {cleaner.get('calendar_integration_enabled')}")
                    
                    # Check for missing fields
                    if not cleaner.get('first_name') or not cleaner.get('last_name'):
                        print(f"      ⚠️  Missing required fields!")
                
                return True, cleaners
            else:
                self.log_result("Get All Cleaners", False, 
                    f"Status: {response.status_code}")
                return False, []
        except Exception as e:
            self.log_result("Get All Cleaners", False, str(e))
            return False, []
    
    def test_get_all_bookings(self):
        """Test GET /api/admin/bookings"""
        print("\n=== Test Get All Bookings ===")
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{BASE_URL}/admin/bookings", headers=headers)
            
            if response.status_code == 200:
                bookings = response.json()
                self.log_result("Get All Bookings", True, f"Found {len(bookings)} bookings")
                
                # Analyze booking assignments
                assigned_count = 0
                unassigned_count = 0
                
                for booking in bookings:
                    if booking.get('cleaner_id'):
                        assigned_count += 1
                        print(f"   ✅ Booking {booking['id'][:8]}: Assigned to {booking.get('cleaner_id')[:8]}")
                    else:
                        unassigned_count += 1
                        print(f"   ⚠️  Booking {booking['id'][:8]}: UNASSIGNED")
                
                print(f"\n   Summary: {assigned_count} assigned, {unassigned_count} unassigned")
                
                return True, bookings
            else:
                self.log_result("Get All Bookings", False, 
                    f"Status: {response.status_code}")
                return False, []
        except Exception as e:
            self.log_result("Get All Bookings", False, str(e))
            return False, []
    
    def test_calendar_integration_status(self):
        """Check calendar integration status for cleaners"""
        print("\n=== Test Calendar Integration Status ===")
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{BASE_URL}/admin/cleaners", headers=headers)
            
            if response.status_code == 200:
                cleaners = response.json()
                
                calendar_enabled_count = 0
                calendar_disabled_count = 0
                
                for cleaner in cleaners:
                    if cleaner.get('calendar_integration_enabled'):
                        calendar_enabled_count += 1
                        print(f"   ✅ {cleaner.get('first_name')} {cleaner.get('last_name')}: Calendar ENABLED")
                        # Check if has credentials
                        has_creds = bool(cleaner.get('google_calendar_credentials'))
                        print(f"      Has credentials: {has_creds}")
                    else:
                        calendar_disabled_count += 1
                        print(f"   ⚠️  {cleaner.get('first_name')} {cleaner.get('last_name')}: Calendar DISABLED")
                
                print(f"\n   Summary: {calendar_enabled_count} enabled, {calendar_disabled_count} disabled")
                
                self.log_result("Calendar Integration Status", True,
                    f"{calendar_enabled_count}/{len(cleaners)} cleaners have calendar enabled")
                
                return True
            else:
                self.log_result("Calendar Integration Status", False,
                    f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Calendar Integration Status", False, str(e))
            return False
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if "✅" in r["status"])
        failed_tests = total_tests - passed_tests
        
        for result in self.test_results:
            print(f"{result['status']} - {result['test']}")
        
        print(f"\nTotal: {total_tests} tests")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")

def main():
    print("="*60)
    print("CALENDAR JOB ASSIGNMENT COMPREHENSIVE TEST")
    print("="*60)
    
    tester = CalendarTester()
    
    # Run tests
    if not tester.admin_login():
        print("❌ Failed to login as admin. Exiting.")
        return
    
    # Test calendar functionality
    tester.test_get_all_cleaners()
    tester.test_get_all_bookings()
    tester.test_get_unassigned_jobs()
    tester.test_get_availability_summary()
    tester.test_calendar_integration_status()
    
    # Print summary
    tester.print_summary()
    
    print("\n" + "="*60)
    print("IDENTIFIED ISSUES:")
    print("="*60)
    print("1. Check if cleaners have missing first_name/last_name fields")
    print("2. Check if bookings are properly assigned to cleaners")
    print("3. Check if calendar integration is enabled for cleaners")
    print("4. Check if existing jobs are showing in availability summary")
    print("5. Check Google Calendar OAuth configuration")

if __name__ == "__main__":
    main()

