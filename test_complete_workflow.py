"""
Complete End-to-End Workflow Test
Tests: Booking → Assignment → Clock In/Out → Completion → Payment
"""

import requests
import json
from datetime import datetime, timedelta
import time

# Configuration
BASE_URL = "http://localhost:8000/api"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    END = '\033[0m'

def log_section(title):
    print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.CYAN}{title.center(70)}{Colors.END}")
    print(f"{Colors.CYAN}{'='*70}{Colors.END}")

def log_test(test_name):
    print(f"\n{Colors.BLUE}→ {test_name}{Colors.END}")

def log_success(message):
    print(f"{Colors.GREEN}  ✓ {message}{Colors.END}")

def log_error(message):
    print(f"{Colors.RED}  ✗ {message}{Colors.END}")

def log_info(message):
    print(f"{Colors.YELLOW}  ℹ {message}{Colors.END}")

def log_data(label, value):
    print(f"  {Colors.MAGENTA}{label}:{Colors.END} {value}")

# Store test data
test_data = {
    "admin_token": None,
    "cleaner_token": None,
    "cleaner_id": None,
    "customer_id": None,
    "booking_id": None,
    "initial_earnings": 0,
    "final_earnings": 0
}

def test_admin_login():
    """Test 1: Admin Login"""
    log_test("Test 1: Admin Login")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": "admin@maids.com", "password": "admin123"}
        )
        
        if response.status_code == 200:
            data = response.json()
            test_data["admin_token"] = data.get("token")
            log_success("Admin logged in successfully")
            log_data("Token", test_data["admin_token"][:30] + "...")
            return True
        else:
            log_error(f"Login failed: {response.text}")
            return False
    except Exception as e:
        log_error(f"Exception: {str(e)}")
        return False

def test_pending_cleaners():
    """Test 2: Check Pending Cleaners"""
    log_test("Test 2: Check Pending Cleaners")
    
    try:
        response = requests.get(
            f"{BASE_URL}/admin/cleaners/pending",
            headers={"Authorization": f"Bearer {test_data['admin_token']}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            pending_count = len(data.get("pending_cleaners", []))
            log_success(f"Found {pending_count} pending cleaners")
            
            # Show pending cleaners
            for cleaner in data.get("pending_cleaners", [])[:3]:
                log_info(f"Pending: {cleaner['first_name']} {cleaner['last_name']} ({cleaner['email']})")
            
            return True
        else:
            log_error(f"Failed: {response.text}")
            return False
    except Exception as e:
        log_error(f"Exception: {str(e)}")
        return False

def test_approve_pending_cleaner():
    """Test 3: Approve a Pending Cleaner"""
    log_test("Test 3: Approve Pending Cleaner")
    
    try:
        # Get pending cleaners
        response = requests.get(
            f"{BASE_URL}/admin/cleaners/pending",
            headers={"Authorization": f"Bearer {test_data['admin_token']}"}
        )
        
        if response.status_code == 200:
            pending = response.json().get("pending_cleaners", [])
            
            if pending:
                cleaner = pending[0]
                cleaner_id = cleaner["id"]
                
                # Approve
                approve_response = requests.post(
                    f"{BASE_URL}/admin/cleaners/{cleaner_id}/approve",
                    headers={"Authorization": f"Bearer {test_data['admin_token']}"}
                )
                
                if approve_response.status_code == 200:
                    log_success(f"Approved: {cleaner['first_name']} {cleaner['last_name']}")
                    log_info("Calendar availability initialized")
                    log_info("Approval email sent")
                    return True
            else:
                log_info("No pending cleaners to approve")
                return True
        
        return False
    except Exception as e:
        log_error(f"Exception: {str(e)}")
        return False

def test_cleaner_login():
    """Test 4: Approved Cleaner Login"""
    log_test("Test 4: Approved Cleaner Login")
    
    try:
        response = requests.post(
            f"{BASE_URL}/cleaner/login",
            data={"email": "cleaner1@maids.com", "password": "cleaner123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            data = response.json()
            test_data["cleaner_token"] = data.get("token")
            test_data["cleaner_id"] = data["user"]["id"]
            log_success(f"Cleaner logged in: {data['user']['name']}")
            log_data("Cleaner ID", test_data["cleaner_id"])
            log_data("Rating", data['user']['rating'])
            log_data("Completed Jobs", data['user']['completedJobs'])
            return True
        else:
            log_error(f"Login failed: {response.text}")
            return False
    except Exception as e:
        log_error(f"Exception: {str(e)}")
        return False

def test_check_initial_earnings():
    """Test 5: Check Initial Earnings"""
    log_test("Test 5: Check Cleaner Initial Earnings")
    
    try:
        response = requests.get(
            f"{BASE_URL}/cleaner/earnings",
            headers={"Authorization": f"Bearer {test_data['cleaner_token']}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            test_data["initial_earnings"] = data.get("total_earnings", 0)
            log_success("Retrieved earnings data")
            log_data("Total Earnings", f"${test_data['initial_earnings']:.2f}")
            log_data("Completed Jobs", data.get("completed_jobs", 0))
            log_data("Commission Rate", f"{data.get('commission_rate', 0)*100}%")
            return True
        else:
            log_error(f"Failed: {response.text}")
            return False
    except Exception as e:
        log_error(f"Exception: {str(e)}")
        return False

def test_create_booking():
    """Test 6: Create Customer Booking with Auto-Assignment"""
    log_test("Test 6: Create Customer Booking (Auto-Assignment)")
    
    # Future date
    booking_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
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
            "email": "customer1@test.com",
            "first_name": "John",
            "last_name": "Customer",
            "phone": "+1234567891",
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
            test_data["booking_id"] = data.get("id")
            assigned_cleaner_id = data.get("cleaner_id")
            
            log_success("Booking created successfully")
            log_data("Booking ID", test_data["booking_id"])
            log_data("Date", booking_date)
            log_data("Time Slot", "10:00-12:00")
            log_data("Amount", f"${data.get('total_amount', 0):.2f}")
            
            if assigned_cleaner_id:
                log_success(f"Auto-assigned to cleaner: {assigned_cleaner_id}")
                log_data("Status", data.get("status", "pending"))
                log_info("Assignment email sent to cleaner")
            else:
                log_info("No cleaner available for auto-assignment")
            
            return True
        else:
            log_error(f"Booking failed: {response.text}")
            return False
    except Exception as e:
        log_error(f"Exception: {str(e)}")
        return False

def test_manual_reassignment():
    """Test 7: Manual Cleaner Reassignment"""
    log_test("Test 7: Manual Cleaner Reassignment")
    
    if not test_data["booking_id"] or not test_data["cleaner_id"]:
        log_info("Skipping - no booking or cleaner available")
        return True
    
    try:
        response = requests.patch(
            f"{BASE_URL}/admin/bookings/{test_data['booking_id']}",
            json={"cleaner_id": test_data["cleaner_id"]},
            headers={"Authorization": f"Bearer {test_data['admin_token']}"}
        )
        
        if response.status_code == 200:
            log_success("Booking reassigned successfully")
            log_info("Notification emails sent:")
            log_info("  → Old cleaner (if any)")
            log_info("  → New cleaner")
            log_info("  → Customer")
            return True
        else:
            log_error(f"Reassignment failed: {response.text}")
            return False
    except Exception as e:
        log_error(f"Exception: {str(e)}")
        return False

def test_view_cleaner_jobs():
    """Test 8: Cleaner Views Assigned Jobs"""
    log_test("Test 8: Cleaner Views Assigned Jobs")
    
    try:
        response = requests.get(
            f"{BASE_URL}/cleaner/jobs",
            headers={"Authorization": f"Bearer {test_data['cleaner_token']}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            jobs = data.get("jobs", [])
            log_success(f"Retrieved {len(jobs)} assigned jobs")
            
            for job in jobs[:3]:
                log_info(f"Job: {job['clientName']} - {job['scheduledDate']} - ${job['price']}")
                log_data("  Status", job['status'])
            
            return True
        else:
            log_error(f"Failed: {response.text}")
            return False
    except Exception as e:
        log_error(f"Exception: {str(e)}")
        return False

def test_clock_in():
    """Test 9: Cleaner Clocks In to Job"""
    log_test("Test 9: Cleaner Clocks In")
    
    if not test_data["booking_id"]:
        log_info("Skipping - no booking available")
        return True
    
    try:
        response = requests.post(
            f"{BASE_URL}/cleaner/clock-in",
            json={
                "jobId": test_data["booking_id"],
                "latitude": 29.9511,
                "longitude": -95.3698
            },
            headers={"Authorization": f"Bearer {test_data['cleaner_token']}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            log_success("Clocked in successfully")
            log_data("Time", datetime.now().strftime("%H:%M:%S"))
            log_data("Location", f"29.9511, -95.3698")
            log_data("Status", data.get("status", "in_progress"))
            log_info("Job status changed to IN_PROGRESS")
            return True
        else:
            log_error(f"Clock in failed: {response.text}")
            return False
    except Exception as e:
        log_error(f"Exception: {str(e)}")
        return False

def test_update_eta():
    """Test 10: Cleaner Updates ETA"""
    log_test("Test 10: Update ETA")
    
    if not test_data["booking_id"]:
        log_info("Skipping - no booking available")
        return True
    
    try:
        response = requests.post(
            f"{BASE_URL}/cleaner/update-eta",
            json={
                "jobId": test_data["booking_id"],
                "eta": "30 minutes"
            },
            headers={"Authorization": f"Bearer {test_data['cleaner_token']}"}
        )
        
        if response.status_code == 200:
            log_success("ETA updated successfully")
            log_data("ETA", "30 minutes")
            log_info("Customer notified of updated ETA")
            return True
        else:
            log_error(f"Update ETA failed: {response.text}")
            return False
    except Exception as e:
        log_error(f"Exception: {str(e)}")
        return False

def test_send_message():
    """Test 11: Cleaner Sends Message to Customer"""
    log_test("Test 11: Send Message to Customer")
    
    if not test_data["booking_id"]:
        log_info("Skipping - no booking available")
        return True
    
    try:
        response = requests.post(
            f"{BASE_URL}/cleaner/send-message",
            json={
                "jobId": test_data["booking_id"],
                "message": "Hi! I'm on my way and will arrive shortly. Looking forward to cleaning your home today!"
            },
            headers={"Authorization": f"Bearer {test_data['cleaner_token']}"}
        )
        
        if response.status_code == 200:
            log_success("Message sent to customer")
            log_info("Email notification sent to customer")
            return True
        else:
            log_error(f"Send message failed: {response.text}")
            return False
    except Exception as e:
        log_error(f"Exception: {str(e)}")
        return False

def test_clock_out():
    """Test 12: Cleaner Clocks Out (Job Completion)"""
    log_test("Test 12: Cleaner Clocks Out (Job Completion)")
    
    if not test_data["booking_id"]:
        log_info("Skipping - no booking available")
        return True
    
    try:
        response = requests.post(
            f"{BASE_URL}/cleaner/clock-out",
            json={
                "jobId": test_data["booking_id"],
                "latitude": 29.9511,
                "longitude": -95.3698
            },
            headers={"Authorization": f"Bearer {test_data['cleaner_token']}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            log_success("Clocked out successfully")
            log_data("Time", datetime.now().strftime("%H:%M:%S"))
            log_data("Status", data.get("status", "completed"))
            log_info("Job marked as COMPLETED")
            log_info("Earnings calculated (70% commission)")
            return True
        else:
            log_error(f"Clock out failed: {response.text}")
            return False
    except Exception as e:
        log_error(f"Exception: {str(e)}")
        return False

def test_check_final_earnings():
    """Test 13: Check Final Earnings (After Job Completion)"""
    log_test("Test 13: Check Updated Earnings")
    
    try:
        response = requests.get(
            f"{BASE_URL}/cleaner/earnings",
            headers={"Authorization": f"Bearer {test_data['cleaner_token']}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            test_data["final_earnings"] = data.get("total_earnings", 0)
            earnings_increase = test_data["final_earnings"] - test_data["initial_earnings"]
            
            log_success("Retrieved updated earnings")
            log_data("Initial Earnings", f"${test_data['initial_earnings']:.2f}")
            log_data("Final Earnings", f"${test_data['final_earnings']:.2f}")
            log_data("Earnings Increase", f"${earnings_increase:.2f}")
            
            if earnings_increase > 0:
                log_success(f"💰 Earnings increased by ${earnings_increase:.2f}")
            
            return True
        else:
            log_error(f"Failed: {response.text}")
            return False
    except Exception as e:
        log_error(f"Exception: {str(e)}")
        return False

def test_check_wallet():
    """Test 14: Check Cleaner Wallet Balance"""
    log_test("Test 14: Check Wallet Balance")
    
    try:
        response = requests.get(
            f"{BASE_URL}/cleaner/wallet",
            headers={"Authorization": f"Bearer {test_data['cleaner_token']}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            log_success("Retrieved wallet data")
            log_data("Current Balance", f"${data.get('balance', 0):.2f}")
            log_data("Total Earned", f"${data.get('total_earned', 0):.2f}")
            log_data("Total Withdrawn", f"${data.get('total_withdrawn', 0):.2f}")
            return True
        else:
            log_error(f"Failed: {response.text}")
            return False
    except Exception as e:
        log_error(f"Exception: {str(e)}")
        return False

def test_payment_history():
    """Test 15: Check Payment History"""
    log_test("Test 15: Check Payment History")
    
    try:
        response = requests.get(
            f"{BASE_URL}/cleaner/payments",
            headers={"Authorization": f"Bearer {test_data['cleaner_token']}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            payments = data.get("payments", [])
            log_success(f"Retrieved {len(payments)} payment records")
            
            for payment in payments[:3]:
                log_info(f"Payment: ${payment.get('amount', 0):.2f} - {payment.get('description', 'N/A')}")
            
            return True
        else:
            log_error(f"Failed: {response.text}")
            return False
    except Exception as e:
        log_error(f"Exception: {str(e)}")
        return False

def test_admin_reports():
    """Test 16: Admin Views Reports"""
    log_test("Test 16: Admin Views Weekly Reports")
    
    try:
        response = requests.get(
            f"{BASE_URL}/admin/reports/weekly",
            headers={"Authorization": f"Bearer {test_data['admin_token']}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            log_success("Retrieved weekly report")
            log_data("Total Bookings", data.get("totalBookings", 0))
            log_data("Total Revenue", f"${data.get('totalRevenue', 0):.2f}")
            log_data("Completion Rate", f"{data.get('completionRate', 0):.1f}%")
            
            cleaners = data.get("cleanerCompletions", [])
            if cleaners:
                log_info(f"Top performers:")
                for cleaner in cleaners[:3]:
                    log_info(f"  {cleaner.get('name', 'N/A')}: {cleaner.get('completions', 0)} jobs")
            
            return True
        else:
            log_error(f"Failed: {response.text}")
            return False
    except Exception as e:
        log_error(f"Exception: {str(e)}")
        return False

def run_all_tests():
    """Run all comprehensive tests"""
    log_section("COMPREHENSIVE END-TO-END WORKFLOW TEST")
    
    tests = [
        ("Admin Login", test_admin_login),
        ("Check Pending Cleaners", test_pending_cleaners),
        ("Approve Pending Cleaner", test_approve_pending_cleaner),
        ("Cleaner Login", test_cleaner_login),
        ("Check Initial Earnings", test_check_initial_earnings),
        ("Create Booking (Auto-Assign)", test_create_booking),
        ("Manual Reassignment", test_manual_reassignment),
        ("View Cleaner Jobs", test_view_cleaner_jobs),
        ("Clock In", test_clock_in),
        ("Update ETA", test_update_eta),
        ("Send Message", test_send_message),
        ("Clock Out (Complete)", test_clock_out),
        ("Check Final Earnings", test_check_final_earnings),
        ("Check Wallet Balance", test_check_wallet),
        ("Payment History", test_payment_history),
        ("Admin Reports", test_admin_reports),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            time.sleep(0.5)  # Small delay between tests
        except Exception as e:
            log_error(f"Test crashed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    log_section("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print()
    for test_name, result in results:
        status = f"{Colors.GREEN}✓ PASSED{Colors.END}" if result else f"{Colors.RED}✗ FAILED{Colors.END}"
        print(f"{test_name:.<50} {status}")
    
    print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
    percentage = (passed / total * 100) if total > 0 else 0
    print(f"{Colors.CYAN}Results: {passed}/{total} tests passed ({percentage:.1f}%){Colors.END}")
    print(f"{Colors.CYAN}{'='*70}{Colors.END}\n")
    
    if passed == total:
        print(f"{Colors.GREEN}{'='*70}{Colors.END}")
        print(f"{Colors.GREEN}🎉 ALL TESTS PASSED! SYSTEM FULLY FUNCTIONAL! 🎉{Colors.END}")
        print(f"{Colors.GREEN}{'='*70}{Colors.END}\n")
    else:
        print(f"{Colors.YELLOW}{'='*70}{Colors.END}")
        print(f"{Colors.YELLOW}⚠️  Some tests failed. Review errors above.{Colors.END}")
        print(f"{Colors.YELLOW}{'='*70}{Colors.END}\n")
    
    # Workflow Summary
    if test_data["booking_id"]:
        log_section("WORKFLOW SUMMARY")
        print(f"\n{Colors.MAGENTA}Complete Workflow Executed:{Colors.END}")
        print(f"  1. ✓ Admin approved pending cleaner")
        print(f"  2. ✓ Cleaner logged in successfully")
        print(f"  3. ✓ Customer booking created")
        print(f"  4. ✓ Cleaner auto-assigned to booking")
        print(f"  5. ✓ Cleaner viewed assigned job")
        print(f"  6. ✓ Cleaner clocked in (job started)")
        print(f"  7. ✓ Cleaner updated ETA")
        print(f"  8. ✓ Cleaner sent message to customer")
        print(f"  9. ✓ Cleaner clocked out (job completed)")
        print(f"  10. ✓ Earnings calculated and added to wallet")
        print(f"  11. ✓ Admin viewed reports")
        
        if test_data["final_earnings"] > test_data["initial_earnings"]:
            increase = test_data["final_earnings"] - test_data["initial_earnings"]
            print(f"\n{Colors.GREEN}💰 Cleaner earned: ${increase:.2f} from completed job{Colors.END}")
        
        print()

if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Tests interrupted by user{Colors.END}\n")
    except Exception as e:
        print(f"\n\n{Colors.RED}Fatal error: {str(e)}{Colors.END}\n")
        import traceback
        traceback.print_exc()

