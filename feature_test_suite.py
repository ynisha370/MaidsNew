#!/usr/bin/env python3
"""
Feature Test Suite
Comprehensive testing of all system features except Twilio
"""

import asyncio
import requests
import json
from datetime import datetime, timezone, timedelta
import time

# Configuration
BACKEND_URL = "http://localhost:8000/api"
ADMIN_URL = "http://localhost:8000/admin"

class FeatureTestSuite:
    def __init__(self):
        self.test_results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "details": []
        }
        self.cleaner_tokens = {}
        self.admin_token = None

    def log_test(self, test_name, status, message="", response_data=None):
        """Log test results"""
        self.test_results["total_tests"] += 1
        if status == "PASS":
            self.test_results["passed"] += 1
            print(f"✅ {test_name}: {message}")
        else:
            self.test_results["failed"] += 1
            print(f"❌ {test_name}: {message}")
        
        self.test_results["details"].append({
            "test": test_name,
            "status": status,
            "message": message,
            "response_data": response_data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

    async def test_cleaner_authentication(self):
        """Test cleaner login and authentication"""
        print("\n🔐 Testing Cleaner Authentication...")
        
        demo_cleaners = [
            {"email": "cleaner1@maids.com", "password": "cleaner123", "name": "Maria Garcia"},
            {"email": "cleaner2@maids.com", "password": "cleaner123", "name": "James Wilson"},
            {"email": "cleaner3@maids.com", "password": "cleaner123", "name": "Lisa Chen"},
            {"email": "sarah.johnson@maids.com", "password": "cleaner123", "name": "Sarah Johnson"},
            {"email": "maria.garcia@maids.com", "password": "cleaner123", "name": "Maria Garcia"}
        ]
        
        for cleaner in demo_cleaners:
            try:
                response = requests.post(f"{BACKEND_URL}/cleaner/login", params={
                    "email": cleaner["email"],
                    "password": cleaner["password"]
                })
                
                if response.status_code == 200:
                    data = response.json()
                    if "token" in data and "user" in data:
                        self.cleaner_tokens[cleaner["email"]] = data["token"]
                        self.log_test(f"Cleaner Login - {cleaner['name']}", "PASS", 
                                    f"Login successful, token received")
                    else:
                        self.log_test(f"Cleaner Login - {cleaner['name']}", "FAIL", 
                                    "Invalid response format")
                else:
                    self.log_test(f"Cleaner Login - {cleaner['name']}", "FAIL", 
                                f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test(f"Cleaner Login - {cleaner['name']}", "FAIL", f"Exception: {str(e)}")

    async def test_cleaner_job_management(self):
        """Test cleaner job viewing and management features"""
        print("\n📋 Testing Cleaner Job Management...")
        
        if not self.cleaner_tokens:
            self.log_test("Cleaner Job Management", "FAIL", "No cleaner tokens available")
            return
        
        # Test with first available cleaner
        cleaner_email = list(self.cleaner_tokens.keys())[0]
        token = self.cleaner_tokens[cleaner_email]
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            # Test get jobs
            jobs_response = requests.get(f"{BACKEND_URL}/cleaner/jobs", headers=headers)
            if jobs_response.status_code == 200:
                jobs_data = jobs_response.json()
                # Handle both list and dict responses
                if isinstance(jobs_data, list):
                    job_count = len(jobs_data)
                else:
                    job_count = len(jobs_data.get('jobs', []))
                self.log_test("Cleaner Jobs View", "PASS", f"Retrieved {job_count} jobs")
            else:
                self.log_test("Cleaner Jobs View", "FAIL", f"HTTP {jobs_response.status_code}: {jobs_response.text}")
            
            # Test get profile
            profile_response = requests.get(f"{BACKEND_URL}/cleaner/profile", headers=headers)
            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                self.log_test("Cleaner Profile", "PASS", f"Profile retrieved: {profile_data.get('name', 'Unknown')}")
            else:
                self.log_test("Cleaner Profile", "FAIL", f"HTTP {profile_response.status_code}: {profile_response.text}")
            
            # Test earnings
            earnings_response = requests.get(f"{BACKEND_URL}/cleaner/earnings", headers=headers)
            if earnings_response.status_code == 200:
                earnings_data = earnings_response.json()
                self.log_test("Cleaner Earnings", "PASS", "Earnings data retrieved successfully")
            else:
                self.log_test("Cleaner Earnings", "FAIL", f"HTTP {earnings_response.status_code}: {earnings_response.text}")
            
            # Test wallet
            wallet_response = requests.get(f"{BACKEND_URL}/cleaner/wallet", headers=headers)
            if wallet_response.status_code == 200:
                wallet_data = wallet_response.json()
                self.log_test("Cleaner Wallet", "PASS", "Wallet data retrieved successfully")
            else:
                self.log_test("Cleaner Wallet", "FAIL", f"HTTP {wallet_response.status_code}: {wallet_response.text}")
            
            # Test payments history
            payments_response = requests.get(f"{BACKEND_URL}/cleaner/payments", headers=headers)
            if payments_response.status_code == 200:
                payments_data = payments_response.json()
                self.log_test("Cleaner Payments", "PASS", "Payment history retrieved successfully")
            else:
                self.log_test("Cleaner Payments", "FAIL", f"HTTP {payments_response.status_code}: {payments_response.text}")
                
        except Exception as e:
            self.log_test("Cleaner Job Management", "FAIL", f"Exception: {str(e)}")

    async def test_cleaner_clock_in_out(self):
        """Test cleaner clock in/out functionality"""
        print("\n⏰ Testing Cleaner Clock In/Out...")
        
        if not self.cleaner_tokens:
            self.log_test("Cleaner Clock In/Out", "FAIL", "No cleaner tokens available")
            return
        
        cleaner_email = list(self.cleaner_tokens.keys())[0]
        token = self.cleaner_tokens[cleaner_email]
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            # First get jobs to find a booking ID
            jobs_response = requests.get(f"{BACKEND_URL}/cleaner/jobs", headers=headers)
            if jobs_response.status_code != 200:
                self.log_test("Cleaner Clock In/Out", "FAIL", "Could not retrieve jobs for clock in/out test")
                return
            
            jobs_data = jobs_response.json()
            jobs = jobs_data.get('jobs', [])
            
            if not jobs:
                self.log_test("Cleaner Clock In/Out", "FAIL", "No jobs available for clock in/out test")
                return
            
            # Use first job for testing
            test_job = jobs[0]
            booking_id = test_job.get('id')
            
            # Test clock in
            clock_in_response = requests.post(f"{BACKEND_URL}/cleaner/clock-in", 
                json={
                    "booking_id": booking_id,
                    "latitude": 29.7604,
                    "longitude": -95.3698
                },
                headers=headers
            )
            if clock_in_response.status_code == 200:
                self.log_test("Cleaner Clock In", "PASS", "Clock in successful")
            else:
                self.log_test("Cleaner Clock In", "FAIL", f"HTTP {clock_in_response.status_code}: {clock_in_response.text}")
            
            # Test ETA update
            eta_response = requests.post(f"{BACKEND_URL}/cleaner/update-eta", 
                json={
                    "booking_id": booking_id,
                    "eta_minutes": 15
                },
                headers=headers
            )
            if eta_response.status_code == 200:
                self.log_test("Cleaner ETA Update", "PASS", "ETA update successful")
            else:
                self.log_test("Cleaner ETA Update", "FAIL", f"HTTP {eta_response.status_code}: {eta_response.text}")
            
            # Test send message
            message_response = requests.post(f"{BACKEND_URL}/cleaner/send-message", 
                json={
                    "booking_id": booking_id,
                    "message": "On my way! ETA 15 minutes."
                },
                headers=headers
            )
            if message_response.status_code == 200:
                self.log_test("Cleaner Send Message", "PASS", "Message sent successfully")
            else:
                self.log_test("Cleaner Send Message", "FAIL", f"HTTP {message_response.status_code}: {message_response.text}")
            
            # Test clock out
            clock_out_response = requests.post(f"{BACKEND_URL}/cleaner/clock-out", 
                json={
                    "booking_id": booking_id,
                    "latitude": 29.7604,
                    "longitude": -95.3698
                },
                headers=headers
            )
            if clock_out_response.status_code == 200:
                self.log_test("Cleaner Clock Out", "PASS", "Clock out successful")
            else:
                self.log_test("Cleaner Clock Out", "FAIL", f"HTTP {clock_out_response.status_code}: {clock_out_response.text}")
                
        except Exception as e:
            self.log_test("Cleaner Clock In/Out", "FAIL", f"Exception: {str(e)}")

    async def test_customer_booking_system(self):
        """Test customer booking and guest checkout"""
        print("\n🛒 Testing Customer Booking System...")
        
        try:
            # Test calendar availability
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            availability_response = requests.get(f"{BACKEND_URL}/calendar/available-dates?start_date={tomorrow}&end_date={tomorrow}")
            if availability_response.status_code == 200:
                availability_data = availability_response.json()
                self.log_test("Calendar Availability", "PASS", f"Availability retrieved for {tomorrow}")
            else:
                self.log_test("Calendar Availability", "FAIL", f"HTTP {availability_response.status_code}: {availability_response.text}")
            
            # Test time slots for specific date
            time_slots_response = requests.get(f"{BACKEND_URL}/calendar/time-slots/{tomorrow}")
            if time_slots_response.status_code == 200:
                time_slots_data = time_slots_response.json()
                self.log_test("Time Slots Retrieval", "PASS", f"Time slots retrieved for {tomorrow}")
            else:
                self.log_test("Time Slots Retrieval", "FAIL", f"HTTP {time_slots_response.status_code}: {time_slots_response.text}")
            
            # Test guest checkout
            guest_booking_data = {
                "customer": {
                    "email": "guest.test@example.com",
                    "first_name": "Guest",
                    "last_name": "Test",
                    "phone": "(281) 555-9999",
                    "address": "999 Test St",
                    "city": "Houston",
                    "state": "TX",
                    "zip_code": "77433"
                },
                "house_size": "1500-2000",
                "frequency": "one_time",
                "services": [{"service_id": "standard_cleaning", "quantity": 1}],
                "a_la_carte_services": [],
                "booking_date": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
                "time_slot": "10:00-13:00",
                "base_price": 120.0,
                "address": {
                    "street": "999 Test St",
                    "city": "Houston",
                    "state": "TX",
                    "zip_code": "77001"
                },
                "special_instructions": "Test guest booking for feature testing"
            }
            
            guest_response = requests.post(f"{BACKEND_URL}/bookings/guest", json=guest_booking_data)
            if guest_response.status_code == 200:
                guest_data = guest_response.json()
                self.log_test("Guest Checkout", "PASS", f"Guest booking created: {guest_data.get('id', 'Unknown')}")
            else:
                self.log_test("Guest Checkout", "FAIL", f"HTTP {guest_response.status_code}: {guest_response.text}")
                
        except Exception as e:
            self.log_test("Customer Booking System", "FAIL", f"Exception: {str(e)}")

    async def test_admin_authentication(self):
        """Test admin login and authentication"""
        print("\n👨‍💼 Testing Admin Authentication...")
        
        try:
            admin_response = requests.post(f"{BACKEND_URL}/auth/login", json={
                "email": "admin@maids.com",
                "password": "admin123"
            })
            
            if admin_response.status_code == 200:
                admin_data = admin_response.json()
                if "access_token" in admin_data:
                    self.admin_token = admin_data["access_token"]
                    self.log_test("Admin Login", "PASS", "Admin login successful")
                else:
                    self.log_test("Admin Login", "FAIL", "No access token in response")
            else:
                self.log_test("Admin Login", "FAIL", f"HTTP {admin_response.status_code}: {admin_response.text}")
                
        except Exception as e:
            self.log_test("Admin Authentication", "FAIL", f"Exception: {str(e)}")

    async def test_admin_dashboard_features(self):
        """Test admin dashboard functionality"""
        print("\n📊 Testing Admin Dashboard Features...")
        
        if not self.admin_token:
            self.log_test("Admin Dashboard", "FAIL", "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # Test get all bookings
            bookings_response = requests.get(f"{BACKEND_URL}/admin/bookings", headers=headers)
            if bookings_response.status_code == 200:
                bookings_data = bookings_response.json()
                booking_count = len(bookings_data.get('bookings', []))
                self.log_test("Admin Bookings View", "PASS", f"Retrieved {booking_count} bookings")
            else:
                self.log_test("Admin Bookings View", "FAIL", f"HTTP {bookings_response.status_code}: {bookings_response.text}")
            
            # Test get all cleaners
            cleaners_response = requests.get(f"{BACKEND_URL}/admin/cleaners", headers=headers)
            if cleaners_response.status_code == 200:
                cleaners_data = cleaners_response.json()
                cleaner_count = len(cleaners_data.get('cleaners', []))
                self.log_test("Admin Cleaners View", "PASS", f"Retrieved {cleaner_count} cleaners")
            else:
                self.log_test("Admin Cleaners View", "FAIL", f"HTTP {cleaners_response.status_code}: {cleaners_response.text}")
            
            # Test calendar overview
            calendar_response = requests.get(f"{BACKEND_URL}/admin/calendar/overview", headers=headers)
            if calendar_response.status_code == 200:
                calendar_data = calendar_response.json()
                self.log_test("Admin Calendar Overview", "PASS", "Calendar overview retrieved successfully")
            else:
                self.log_test("Admin Calendar Overview", "FAIL", f"HTTP {calendar_response.status_code}: {calendar_response.text}")
            
            # Test calendar events
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            next_week = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
            events_response = requests.get(f"{BACKEND_URL}/admin/calendar/events?start_date={tomorrow}&end_date={next_week}", headers=headers)
            if events_response.status_code == 200:
                events_data = events_response.json()
                event_count = len(events_data.get('events', []))
                self.log_test("Admin Calendar Events", "PASS", f"Retrieved {event_count} calendar events")
            else:
                self.log_test("Admin Calendar Events", "FAIL", f"HTTP {events_response.status_code}: {events_response.text}")
            
            # Test reports
            reports_response = requests.get(f"{BACKEND_URL}/admin/reports/orders", headers=headers)
            if reports_response.status_code == 200:
                reports_data = reports_response.json()
                self.log_test("Admin Reports", "PASS", "Reports retrieved successfully")
            else:
                self.log_test("Admin Reports", "FAIL", f"HTTP {reports_response.status_code}: {reports_response.text}")
                
        except Exception as e:
            self.log_test("Admin Dashboard Features", "FAIL", f"Exception: {str(e)}")

    async def test_admin_job_assignment(self):
        """Test admin job assignment functionality"""
        print("\n👥 Testing Admin Job Assignment...")
        
        if not self.admin_token:
            self.log_test("Admin Job Assignment", "FAIL", "No admin token available")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # Get unassigned jobs
            unassigned_response = requests.get(f"{BACKEND_URL}/admin/calendar/unassigned-jobs", headers=headers)
            if unassigned_response.status_code == 200:
                unassigned_data = unassigned_response.json()
                unassigned_count = len(unassigned_data.get('unassigned_jobs', []))
                self.log_test("Admin Unassigned Jobs", "PASS", f"Retrieved {unassigned_count} unassigned jobs")
            else:
                self.log_test("Admin Unassigned Jobs", "FAIL", f"HTTP {unassigned_response.status_code}: {unassigned_response.text}")
            
            # Test cleaner availability
            cleaners_response = requests.get(f"{BACKEND_URL}/admin/cleaners", headers=headers)
            if cleaners_response.status_code == 200:
                cleaners_data = cleaners_response.json()
                cleaners = cleaners_data.get('cleaners', [])
                
                if cleaners:
                    # Test cleaner availability for first cleaner
                    cleaner_id = cleaners[0].get('id')
                    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
                    next_week = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
                    
                    availability_response = requests.get(f"{BACKEND_URL}/admin/calendar/cleaner-availability/{cleaner_id}?start_date={tomorrow}&end_date={next_week}", headers=headers)
                    if availability_response.status_code == 200:
                        availability_data = availability_response.json()
                        self.log_test("Admin Cleaner Availability", "PASS", "Cleaner availability retrieved successfully")
                    else:
                        self.log_test("Admin Cleaner Availability", "FAIL", f"HTTP {availability_response.status_code}: {availability_response.text}")
                
        except Exception as e:
            self.log_test("Admin Job Assignment", "FAIL", f"Exception: {str(e)}")

    async def test_payment_integration(self):
        """Test Stripe payment integration"""
        print("\n💳 Testing Payment Integration...")
        
        try:
            # Test Stripe configuration
            stripe_response = requests.get(f"{BACKEND_URL}/stripe/config")
            if stripe_response.status_code == 200:
                stripe_data = stripe_response.json()
                self.log_test("Stripe Configuration", "PASS", "Stripe config retrieved successfully")
            else:
                self.log_test("Stripe Configuration", "FAIL", f"HTTP {stripe_response.status_code}: {stripe_response.text}")
            
            # Test payment methods (requires authentication)
            if self.admin_token:
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                payment_methods_response = requests.get(f"{BACKEND_URL}/stripe/payment-methods", headers=headers)
                if payment_methods_response.status_code == 200:
                    self.log_test("Stripe Payment Methods", "PASS", "Payment methods retrieved successfully")
                else:
                    self.log_test("Stripe Payment Methods", "FAIL", f"HTTP {payment_methods_response.status_code}: {payment_methods_response.text}")
            else:
                self.log_test("Stripe Payment Methods", "FAIL", "No admin token available")
                
        except Exception as e:
            self.log_test("Payment Integration", "FAIL", f"Exception: {str(e)}")

    async def test_email_reminders(self):
        """Test Amazon SES email integration"""
        print("\n📧 Testing Email Reminders...")
        
        try:
            # Test email service status (requires admin authentication)
            if self.admin_token:
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                email_status_response = requests.get(f"{BACKEND_URL}/admin/email/status", headers=headers)
                if email_status_response.status_code == 200:
                    email_data = email_status_response.json()
                    self.log_test("Email Service Status", "PASS", "Email service status retrieved successfully")
                else:
                    self.log_test("Email Service Status", "FAIL", f"HTTP {email_status_response.status_code}: {email_status_response.text}")
                
                # Test send test email
                test_email_response = requests.post(f"{BACKEND_URL}/admin/email/send-test", 
                    params={
                        "to": "test@example.com",
                        "subject": "Test Email from Maids of Cyfair",
                        "message": "This is a test email to verify email functionality."
                    },
                    headers=headers
                )
                if test_email_response.status_code == 200:
                    self.log_test("Test Email Send", "PASS", "Test email sent successfully")
                else:
                    self.log_test("Test Email Send", "FAIL", f"HTTP {test_email_response.status_code}: {test_email_response.text}")
            else:
                self.log_test("Email Service Status", "FAIL", "No admin token available")
                self.log_test("Test Email Send", "FAIL", "No admin token available")
                
        except Exception as e:
            self.log_test("Email Reminders", "FAIL", f"Exception: {str(e)}")

    async def test_scheduling_engine(self):
        """Test scheduling and order tracking"""
        print("\n📅 Testing Scheduling Engine...")
        
        try:
            # Test availability checking
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            availability_response = requests.get(f"{BACKEND_URL}/availability?date={tomorrow}&time_slot=09:00-12:00")
            if availability_response.status_code == 200:
                availability_data = availability_response.json()
                self.log_test("Availability Check", "PASS", f"Availability check successful: {availability_data.get('message', 'Unknown')}")
            else:
                self.log_test("Availability Check", "FAIL", f"HTTP {availability_response.status_code}: {availability_response.text}")
            
            # Test order tracking (if we have bookings)
            if self.admin_token:
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                bookings_response = requests.get(f"{BACKEND_URL}/admin/bookings", headers=headers)
                if bookings_response.status_code == 200:
                    bookings_data = bookings_response.json()
                    bookings = bookings_data.get('bookings', [])
                    
                    if bookings:
                        # Test tracking for first booking
                        booking_id = bookings[0].get('id')
                        tracking_response = requests.get(f"{BACKEND_URL}/bookings/{booking_id}/track")
                        if tracking_response.status_code == 200:
                            tracking_data = tracking_response.json()
                            self.log_test("Order Tracking", "PASS", "Order tracking retrieved successfully")
                        else:
                            self.log_test("Order Tracking", "FAIL", f"HTTP {tracking_response.status_code}: {tracking_response.text}")
                
        except Exception as e:
            self.log_test("Scheduling Engine", "FAIL", f"Exception: {str(e)}")

    async def test_flutter_app_integration(self):
        """Test Flutter app API endpoints"""
        print("\n📱 Testing Flutter App Integration...")
        
        if not self.cleaner_tokens:
            self.log_test("Flutter App Integration", "FAIL", "No cleaner tokens available")
            return
        
        cleaner_email = list(self.cleaner_tokens.keys())[0]
        token = self.cleaner_tokens[cleaner_email]
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            # Test all Flutter-specific endpoints
            endpoints = [
                ("/cleaner/profile", "Profile Data"),
                ("/cleaner/jobs", "Jobs Data"),
                ("/cleaner/earnings", "Earnings Data"),
                ("/cleaner/wallet", "Wallet Data"),
                ("/cleaner/payments", "Payments Data")
            ]
            
            for endpoint, description in endpoints:
                response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers)
                if response.status_code == 200:
                    self.log_test(f"Flutter {description}", "PASS", f"{description} retrieved successfully")
                else:
                    self.log_test(f"Flutter {description}", "FAIL", f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Flutter App Integration", "FAIL", f"Exception: {str(e)}")

    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*70)
        print("📊 COMPREHENSIVE FEATURE TEST REPORT")
        print("="*70)
        
        total = self.test_results["total_tests"]
        passed = self.test_results["passed"]
        failed = self.test_results["failed"]
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"\n📈 Test Summary:")
        print(f"   Total Tests: {total}")
        print(f"   Passed: {passed}")
        print(f"   Failed: {failed}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        print(f"\n✅ Passed Tests:")
        for test in self.test_results["details"]:
            if test["status"] == "PASS":
                print(f"   - {test['test']}: {test['message']}")
        
        if failed > 0:
            print(f"\n❌ Failed Tests:")
            for test in self.test_results["details"]:
                if test["status"] == "FAIL":
                    print(f"   - {test['test']}: {test['message']}")
        
        # Save detailed report to file
        report_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "total_tests": total,
                "passed": passed,
                "failed": failed,
                "success_rate": success_rate
            },
            "test_details": self.test_results["details"]
        }
        
        report_file = f"feature_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        return success_rate >= 80  # Consider 80%+ success rate as passing

    async def run_all_tests(self):
        """Run all feature tests"""
        print("🚀 Starting Comprehensive Feature Testing")
        print("="*70)
        
        # Run all test categories
        await self.test_cleaner_authentication()
        await self.test_cleaner_job_management()
        await self.test_cleaner_clock_in_out()
        await self.test_customer_booking_system()
        await self.test_admin_authentication()
        await self.test_admin_dashboard_features()
        await self.test_admin_job_assignment()
        await self.test_payment_integration()
        await self.test_email_reminders()
        await self.test_scheduling_engine()
        await self.test_flutter_app_integration()
        
        # Generate report
        success = self.generate_test_report()
        
        if success:
            print("\n🎉 Feature testing completed successfully!")
        else:
            print("\n⚠️  Some feature tests failed. Please review the report.")
        
        return success

async def main():
    """Main function to run feature testing"""
    tester = FeatureTestSuite()
    try:
        success = await tester.run_all_tests()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Test execution failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
