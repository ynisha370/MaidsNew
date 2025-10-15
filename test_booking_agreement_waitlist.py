#!/usr/bin/env python3
"""
Test Booking Agreement and Waitlist Functionality
"""

import requests
import json
from datetime import datetime, timedelta

BACKEND_URL = "http://localhost:8000/api"

def test_booking_agreement():
    """Test booking agreement functionality"""
    print("🔐 Testing Booking Agreement...")
    
    # Test creating a booking agreement
    agreement_data = {
        "customer_id": "test_customer_123",
        "booking_id": "test_booking_123",
        "agreement_accepted": True,
        "ip_address": "192.168.1.1",
        "user_agent": "Mozilla/5.0 Test Browser"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/booking-agreement", json=agreement_data)
        if response.status_code == 200:
            print("✅ Booking agreement created successfully")
            agreement = response.json()
            print(f"   Agreement ID: {agreement['id']}")
            print(f"   Accepted: {agreement['agreement_accepted']}")
            print(f"   Accepted at: {agreement['accepted_at']}")
        else:
            print(f"❌ Failed to create booking agreement: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error creating booking agreement: {str(e)}")

def test_waitlist():
    """Test waitlist functionality"""
    print("\n📋 Testing Waitlist System...")
    
    # Test adding to waitlist
    waitlist_data = {
        "email": "waitlist@example.com",
        "phone": "555-0123",
        "first_name": "Waitlist",
        "last_name": "Customer",
        "preferred_frequency": "weekly",
        "preferred_time_slot": "09:00-12:00",
        "house_size": "3_bedroom",
        "address": {
            "street": "123 Waitlist St",
            "city": "Houston",
            "state": "TX",
            "zip_code": "77433"
        },
        "notes": "Test waitlist entry"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/waitlist", json=waitlist_data)
        if response.status_code == 200:
            print("✅ Added to waitlist successfully")
            entry = response.json()
            print(f"   Waitlist ID: {entry['id']}")
            print(f"   Email: {entry['email']}")
            print(f"   Status: {entry['status']}")
        else:
            print(f"❌ Failed to add to waitlist: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error adding to waitlist: {str(e)}")

def test_capacity_check():
    """Test capacity checking functionality"""
    print("\n📊 Testing Capacity Management...")
    
    # Test capacity check for today
    today = datetime.now().strftime('%Y-%m-%d')
    
    try:
        response = requests.get(f"{BACKEND_URL}/capacity/check", params={"date": today})
        if response.status_code == 200:
            capacity_data = response.json()
            print("✅ Capacity check successful")
            print(f"   Date: {capacity_data['date']}")
            print(f"   Has capacity: {capacity_data['has_capacity']}")
            print(f"   Current bookings: {capacity_data['current_bookings']}")
            print(f"   Max capacity: {capacity_data['max_capacity']}")
            print(f"   Available slots: {capacity_data['available_slots']}")
        else:
            print(f"❌ Failed to check capacity: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error checking capacity: {str(e)}")

def test_capacity_status():
    """Test capacity status for next 30 days"""
    print("\n📅 Testing Capacity Status...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/capacity/status")
        if response.status_code == 200:
            capacity_data = response.json()
            print("✅ Capacity status retrieved successfully")
            print(f"   Retrieved data for {len(capacity_data)} days")
            
            # Show first 5 days
            for i, day_data in enumerate(capacity_data[:5]):
                print(f"   {day_data['date']}: {day_data['current_bookings']}/{day_data['max_capacity']} ({'✅' if day_data['has_capacity'] else '❌'})")
        else:
            print(f"❌ Failed to get capacity status: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error getting capacity status: {str(e)}")

def test_admin_bookings():
    """Test admin bookings endpoint"""
    print("\n👨‍💼 Testing Admin Bookings...")
    
    # First login as admin
    admin_login = requests.post(f"{BACKEND_URL}/auth/login", json={
        "email": "admin@maids.com",
        "password": "admin123"
    })
    
    if admin_login.status_code == 200:
        admin_token = admin_login.json()["access_token"]
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        try:
            response = requests.get(f"{BACKEND_URL}/admin/bookings", headers=headers)
            if response.status_code == 200:
                bookings = response.json()
                print("✅ Admin bookings retrieved successfully")
                print(f"   Found {len(bookings)} bookings")
                
                if bookings:
                    sample_booking = bookings[0]
                    print(f"   Sample booking:")
                    print(f"     ID: {sample_booking.get('id')}")
                    print(f"     House size: {sample_booking.get('house_size')}")
                    print(f"     Payment status: {sample_booking.get('payment_status')}")
                    print(f"     Status: {sample_booking.get('status')}")
            else:
                print(f"❌ Failed to get admin bookings: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Error getting admin bookings: {str(e)}")
    else:
        print(f"❌ Admin login failed: {admin_login.status_code} - {admin_login.text}")

def main():
    """Run all tests"""
    print("🚀 Testing Booking Agreement and Waitlist Functionality")
    print("=" * 60)
    
    test_booking_agreement()
    test_waitlist()
    test_capacity_check()
    test_capacity_status()
    test_admin_bookings()
    
    print("\n" + "=" * 60)
    print("🎉 Testing completed!")

if __name__ == "__main__":
    main()
