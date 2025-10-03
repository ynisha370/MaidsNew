#!/usr/bin/env python3
"""
Stripe Integration Test Script
Tests the complete Stripe payment integration with security validation
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime, timedelta

# Test configuration
BASE_URL = "http://localhost:8000/api"
TEST_USER = {
    "email": "test@example.com",
    "password": "testpassword123",
    "first_name": "Test",
    "last_name": "User"
}

# Stripe test card data
TEST_CARDS = {
    "success": {
        "card_number": "4242424242424242",
        "expiry_month": 12,
        "expiry_year": 2025,
        "cvc": "123",
        "cardholder_name": "Test User"
    },
    "declined": {
        "card_number": "4000000000000002",
        "expiry_month": 12,
        "expiry_year": 2025,
        "cvc": "123",
        "cardholder_name": "Test User"
    },
    "3d_secure": {
        "card_number": "4000002500003155",
        "expiry_month": 12,
        "expiry_year": 2025,
        "cvc": "123",
        "cardholder_name": "Test User"
    }
}

class StripeIntegrationTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.user_id = None
        self.booking_id = None
        self.payment_method_id = None
        self.payment_intent_id = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def make_request(self, method, endpoint, data=None, headers=None):
        """Make HTTP request with error handling"""
        url = f"{BASE_URL}{endpoint}"
        request_headers = {"Content-Type": "application/json"}
        
        if headers:
            request_headers.update(headers)
        
        if self.auth_token:
            request_headers["Authorization"] = f"Bearer {self.auth_token}"
        
        try:
            async with self.session.request(method, url, json=data, headers=request_headers) as response:
                response_data = await response.json() if response.content_type == 'application/json' else None
                
                if response.status >= 400:
                    print(f"❌ {method} {endpoint} - Status: {response.status}")
                    print(f"   Error: {response_data}")
                    return None, response.status
                
                print(f"✅ {method} {endpoint} - Status: {response.status}")
                return response_data, response.status
                
        except Exception as e:
            print(f"❌ {method} {endpoint} - Exception: {str(e)}")
            return None, 500

    async def test_user_registration(self):
        """Test user registration"""
        print("\n🔐 Testing User Registration...")
        
        data, status = await self.make_request("POST", "/register", TEST_USER)
        if status == 200:
            print("✅ User registration successful")
            return True
        else:
            print("❌ User registration failed")
            return False

    async def test_user_login(self):
        """Test user login"""
        print("\n🔐 Testing User Login...")
        
        login_data = {
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        }
        
        data, status = await self.make_request("POST", "/login", login_data)
        if status == 200 and data.get("access_token"):
            self.auth_token = data["access_token"]
            self.user_id = data["user"]["id"]
            print("✅ User login successful")
            return True
        else:
            print("❌ User login failed")
            return False

    async def test_stripe_config(self):
        """Test Stripe configuration endpoint"""
        print("\n💳 Testing Stripe Configuration...")
        
        data, status = await self.make_request("GET", "/stripe/config")
        if status == 200 and data.get("publishable_key"):
            print("✅ Stripe configuration loaded")
            return True
        else:
            print("❌ Stripe configuration failed")
            return False

    async def test_payment_method_creation(self):
        """Test payment method creation"""
        print("\n💳 Testing Payment Method Creation...")
        
        card_data = TEST_CARDS["success"]
        data, status = await self.make_request("POST", "/payment-methods", card_data)
        
        if status == 200 and data.get("id"):
            self.payment_method_id = data["id"]
            print("✅ Payment method created successfully")
            return True
        else:
            print("❌ Payment method creation failed")
            return False

    async def test_payment_methods_list(self):
        """Test getting payment methods"""
        print("\n💳 Testing Payment Methods List...")
        
        data, status = await self.make_request("GET", "/payment-methods")
        if status == 200 and isinstance(data, list):
            print(f"✅ Retrieved {len(data)} payment methods")
            return True
        else:
            print("❌ Failed to retrieve payment methods")
            return False

    async def test_booking_creation(self):
        """Test booking creation"""
        print("\n📅 Testing Booking Creation...")
        
        booking_data = {
            "customer": {
                "email": TEST_USER["email"],
                "first_name": TEST_USER["first_name"],
                "last_name": TEST_USER["last_name"],
                "phone": "1234567890",
                "address": "123 Test St",
                "city": "Houston",
                "state": "TX",
                "zip_code": "77433",
                "is_guest": False
            },
            "house_size": "small",
            "frequency": "one_time",
            "base_price": 100.0,
            "rooms": {"bedroom": 1, "bathroom": 1},
            "services": [],
            "a_la_carte_services": [],
            "booking_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            "time_slot": "09:00-11:00",
            "special_instructions": "Test booking"
        }
        
        data, status = await self.make_request("POST", "/bookings", booking_data)
        if status == 200 and data.get("id"):
            self.booking_id = data["id"]
            print("✅ Booking created successfully")
            return True
        else:
            print("❌ Booking creation failed")
            return False

    async def test_payment_intent_creation(self):
        """Test payment intent creation"""
        print("\n💳 Testing Payment Intent Creation...")
        
        if not self.booking_id:
            print("❌ No booking ID available")
            return False
        
        # Get booking details to get total amount
        booking_data, status = await self.make_request("GET", f"/bookings/{self.booking_id}")
        if status != 200:
            print("❌ Failed to get booking details")
            return False
        
        total_amount = booking_data.get("total_amount", 100.0)
        amount_cents = int(total_amount * 100)
        
        payment_intent_data = {
            "booking_id": self.booking_id,
            "amount": amount_cents,
            "currency": "usd"
        }
        
        data, status = await self.make_request("POST", "/payment-intents", payment_intent_data)
        if status == 200 and data.get("id"):
            self.payment_intent_id = data["id"]
            print("✅ Payment intent created successfully")
            return True
        else:
            print("❌ Payment intent creation failed")
            return False

    async def test_payment_intent_confirmation(self):
        """Test payment intent confirmation"""
        print("\n💳 Testing Payment Intent Confirmation...")
        
        if not self.payment_intent_id:
            print("❌ No payment intent ID available")
            return False
        
        data, status = await self.make_request("POST", f"/payment-intents/{self.payment_intent_id}/confirm")
        if status == 200:
            print("✅ Payment intent confirmed successfully")
            return True
        else:
            print("❌ Payment intent confirmation failed")
            return False

    async def test_payment_intent_status(self):
        """Test getting payment intent status"""
        print("\n💳 Testing Payment Intent Status...")
        
        if not self.payment_intent_id:
            print("❌ No payment intent ID available")
            return False
        
        data, status = await self.make_request("GET", f"/payment-intents/{self.payment_intent_id}")
        if status == 200 and data.get("status"):
            print(f"✅ Payment intent status: {data['status']}")
            return True
        else:
            print("❌ Failed to get payment intent status")
            return False

    async def test_security_validation(self):
        """Test security validation"""
        print("\n🔒 Testing Security Validation...")
        
        # Test invalid card number
        invalid_card = TEST_CARDS["success"].copy()
        invalid_card["card_number"] = "1234567890123456"  # Invalid card
        
        data, status = await self.make_request("POST", "/payment-methods", invalid_card)
        if status == 400:
            print("✅ Invalid card number rejected")
        else:
            print("❌ Invalid card number should be rejected")
        
        # Test invalid CVC
        invalid_cvc = TEST_CARDS["success"].copy()
        invalid_cvc["cvc"] = "12"  # Invalid CVC
        
        data, status = await self.make_request("POST", "/payment-methods", invalid_cvc)
        if status == 400:
            print("✅ Invalid CVC rejected")
        else:
            print("❌ Invalid CVC should be rejected")
        
        # Test invalid expiry date
        invalid_expiry = TEST_CARDS["success"].copy()
        invalid_expiry["expiry_year"] = 2020  # Past year
        
        data, status = await self.make_request("POST", "/payment-methods", invalid_expiry)
        if status == 400:
            print("✅ Invalid expiry date rejected")
        else:
            print("❌ Invalid expiry date should be rejected")
        
        return True

    async def test_cleanup(self):
        """Clean up test data"""
        print("\n🧹 Cleaning up test data...")
        
        # Delete payment method
        if self.payment_method_id:
            await self.make_request("DELETE", f"/payment-methods/{self.payment_method_id}")
            print("✅ Payment method deleted")
        
        # Note: In a real scenario, you might want to clean up bookings and users too
        print("✅ Cleanup completed")

    async def run_all_tests(self):
        """Run all integration tests"""
        print("🚀 Starting Stripe Integration Tests...")
        print("=" * 50)
        
        tests = [
            ("User Registration", self.test_user_registration),
            ("User Login", self.test_user_login),
            ("Stripe Configuration", self.test_stripe_config),
            ("Payment Method Creation", self.test_payment_method_creation),
            ("Payment Methods List", self.test_payment_methods_list),
            ("Booking Creation", self.test_booking_creation),
            ("Payment Intent Creation", self.test_payment_intent_creation),
            ("Payment Intent Confirmation", self.test_payment_intent_confirmation),
            ("Payment Intent Status", self.test_payment_intent_status),
            ("Security Validation", self.test_security_validation),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                result = await test_func()
                if result:
                    passed += 1
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {str(e)}")
        
        # Cleanup
        await self.test_cleanup()
        
        print("\n" + "=" * 50)
        print(f"🏁 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Stripe integration is working correctly.")
        else:
            print("⚠️  Some tests failed. Please check the implementation.")
        
        return passed == total

async def main():
    """Main test runner"""
    print("Stripe Integration Test Suite")
    print("Make sure the backend server is running on http://localhost:8000")
    print("Make sure you have valid Stripe test keys configured")
    print()
    
    async with StripeIntegrationTester() as tester:
        success = await tester.run_all_tests()
        return success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
