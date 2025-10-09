#!/usr/bin/env python3
"""
Test script to check if admin dashboard endpoints are working
"""
import requests
import json

# Backend URL
BACKEND_URL = "http://localhost:8000"
API = f"{BACKEND_URL}/api"

def test_endpoint(endpoint, description):
    """Test a single endpoint"""
    try:
        print(f"\nTesting: {description}")
        print(f"URL: {API}{endpoint}")
        response = requests.get(f"{API}{endpoint}", timeout=5)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"✅ Success - Returned {len(data)} items")
                if len(data) > 0:
                    print(f"Sample: {json.dumps(data[0], indent=2, default=str)[:200]}...")
            else:
                print(f"✅ Success - Data: {json.dumps(data, indent=2, default=str)[:200]}...")
        else:
            print(f"❌ Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection Error: Backend server is not running at {BACKEND_URL}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    print("=" * 80)
    print("Admin Dashboard Endpoint Tests")
    print("=" * 80)
    
    # Test services endpoint (public)
    test_endpoint("/services", "Public Services Endpoint")
    
    # Test admin services endpoint (requires auth)
    test_endpoint("/admin/services", "Admin Services Endpoint")
    
    # Test calendar endpoints
    test_endpoint("/admin/calendar/unassigned-jobs", "Calendar - Unassigned Jobs")
    test_endpoint("/admin/calendar/availability-summary", "Calendar - Availability Summary")
    test_endpoint("/admin/calendar/overview", "Calendar - Overview")
    
    print("\n" + "=" * 80)
    print("Test Complete")
    print("=" * 80)

if __name__ == "__main__":
    main()

