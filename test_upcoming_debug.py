#!/usr/bin/env python3
"""
Debug script to test upcoming appointments endpoint
"""

import requests
import json

def test_upcoming_appointments():
    base_url = "http://localhost:8000/api"
    
    print("🔐 Testing Authentication...")
    
    # Try to login with test credentials
    login_data = {
        "email": "test@maids.com", 
        "password": "test@maids@1234"
    }
    
    try:
        # Login
        login_response = requests.post(f"{base_url}/auth/login", json=login_data, timeout=5)
        print(f"Login Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            auth_data = login_response.json()
            token = auth_data.get("access_token")
            user = auth_data.get("user", {})
            print(f"✅ Login successful for {user.get('first_name', 'Unknown')} {user.get('last_name', 'User')}")
            print(f"User ID: {user.get('id', 'Unknown')}")
            
            # Test upcoming appointments endpoint
            headers = {"Authorization": f"Bearer {token}"}
            print(f"\n📅 Testing upcoming appointments endpoint...")
            
            upcoming_response = requests.get(f"{base_url}/customer/upcoming-appointments", headers=headers, timeout=5)
            print(f"Upcoming Appointments Status: {upcoming_response.status_code}")
            print(f"Response: {upcoming_response.text}")
            
            if upcoming_response.status_code == 200:
                upcoming_data = upcoming_response.json()
                print(f"Upcoming appointments count: {len(upcoming_data) if isinstance(upcoming_data, list) else 'Not a list'}")
                if upcoming_data:
                    print(f"First appointment: {json.dumps(upcoming_data[0], indent=2)}")
            
            # Test next appointment endpoint
            print(f"\n📅 Testing next appointment endpoint...")
            next_response = requests.get(f"{base_url}/customer/next-appointment", headers=headers, timeout=5)
            print(f"Next Appointment Status: {next_response.status_code}")
            print(f"Response: {next_response.text}")
            
        else:
            print(f"❌ Login failed: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_upcoming_appointments()
