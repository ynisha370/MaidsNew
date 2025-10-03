#!/usr/bin/env python3
"""
Test script for Stripe Embedded Checkout integration
"""

import requests
import json
import sys
import os

# Add backend to path
sys.path.append('backend')

def test_create_checkout_session():
    """Test the create-checkout-session endpoint"""
    print("Testing Stripe Embedded Checkout Integration...")
    
    # Test data
    test_booking_id = "test-booking-123"
    test_data = {
        "booking_id": test_booking_id,
        "success_url": "http://localhost:3000",
        "cancel_url": "http://localhost:3000"
    }
    
    try:
        # Test the endpoint
        response = requests.post(
            "http://localhost:8000/api/create-checkout-session",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if "clientSecret" in data:
                print("✅ create-checkout-session endpoint working correctly")
                print(f"Client Secret: {data['clientSecret'][:20]}...")
                return True
            else:
                print("❌ Response missing clientSecret")
                return False
        else:
            print(f"❌ Endpoint returned error: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend server. Make sure it's running on port 8000")
        return False
    except Exception as e:
        print(f"❌ Error testing endpoint: {str(e)}")
        return False

def test_frontend_integration():
    """Test that the frontend components are properly set up"""
    print("\nTesting Frontend Integration...")
    
    # Check if the new component exists
    if os.path.exists("../frontend/src/components/StripeEmbeddedCheckout.js"):
        print("✅ StripeEmbeddedCheckout component created")
    else:
        print("❌ StripeEmbeddedCheckout component not found")
        return False
    
    # Check if PaymentPage was updated
    with open("../frontend/src/components/PaymentPage.js", "r") as f:
        content = f.read()
        if "StripeEmbeddedCheckout" in content:
            print("✅ PaymentPage updated to use StripeEmbeddedCheckout")
        else:
            print("❌ PaymentPage not updated")
            return False
    
    print("✅ Frontend integration looks good")
    return True

def main():
    """Run all tests"""
    print("=" * 50)
    print("STRIPE EMBEDDED CHECKOUT INTEGRATION TEST")
    print("=" * 50)
    
    # Test backend
    backend_ok = test_create_checkout_session()
    
    # Test frontend
    frontend_ok = test_frontend_integration()
    
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    if backend_ok and frontend_ok:
        print("✅ All tests passed! Stripe Embedded Checkout is ready to use.")
        print("\nTo use the new checkout:")
        print("1. Start the backend server: cd backend && python server.py")
        print("2. Start the frontend: cd frontend && npm start")
        print("3. Navigate to a payment page to see the embedded checkout")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        if not backend_ok:
            print("- Backend endpoint needs to be fixed")
        if not frontend_ok:
            print("- Frontend components need to be fixed")

if __name__ == "__main__":
    main()
