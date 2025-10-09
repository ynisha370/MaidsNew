#!/usr/bin/env python3
"""
Test admin authentication and endpoints
"""
import requests
import json

# Backend URL
BACKEND_URL = "http://localhost:8000"
API = f"{BACKEND_URL}/api"

def test_admin_login():
    """Test admin login"""
    print("\n" + "="*80)
    print("Testing Admin Login")
    print("="*80)
    
    # Try to login as admin
    admin_credentials = {
        "email": "admin@maidsofcyfair.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{API}/auth/login", json=admin_credentials)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print(f"✅ Login successful!")
            print(f"Token: {token[:20]}...")
            return token
        else:
            print(f"❌ Login failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def test_admin_endpoints(token):
    """Test admin endpoints with token"""
    if not token:
        print("\n❌ No token available, skipping endpoint tests")
        return
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    print("\n" + "="*80)
    print("Testing Admin Endpoints with Authentication")
    print("="*80)
    
    # Test admin services endpoint
    print("\n1. Testing /admin/services")
    try:
        response = requests.get(f"{API}/admin/services", headers=headers)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success - Returned {len(data)} services")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test calendar endpoints
    print("\n2. Testing /admin/calendar/unassigned-jobs")
    try:
        response = requests.get(f"{API}/admin/calendar/unassigned-jobs", headers=headers)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success - Data: {json.dumps(data, indent=2, default=str)[:200]}...")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print("\n3. Testing /admin/calendar/availability-summary")
    try:
        response = requests.get(f"{API}/admin/calendar/availability-summary", headers=headers)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success - Data: {json.dumps(data, indent=2, default=str)[:200]}...")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print("\n4. Testing /admin/cleaners")
    try:
        response = requests.get(f"{API}/admin/cleaners", headers=headers)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success - Returned {len(data)} cleaners")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print("\n5. Testing /admin/stats")
    try:
        response = requests.get(f"{API}/admin/stats", headers=headers)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success - Stats: {json.dumps(data, indent=2, default=str)[:300]}...")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    # Test login first
    token = test_admin_login()
    
    # Test endpoints with token
    test_admin_endpoints(token)
    
    print("\n" + "="*80)
    print("Test Complete")
    print("="*80)

if __name__ == "__main__":
    main()

