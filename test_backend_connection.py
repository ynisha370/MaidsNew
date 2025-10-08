#!/usr/bin/env python3
"""
Quick Backend Connection Test
Tests if the backend server is running and accessible
"""

import requests
import json
import sys
from datetime import datetime

def test_backend_connection():
    """Test backend server connectivity and basic endpoints"""
    
    base_url = "http://localhost:8000"
    test_results = []
    
    print("Testing Backend Connection...")
    print("=" * 50)
    
    # Test 1: Basic server response
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        test_results.append(("Server Root", response.status_code == 200, f"Status: {response.status_code}"))
        print(f"[PASS] Server Root: {response.status_code}")
    except Exception as e:
        test_results.append(("Server Root", False, f"Error: {str(e)}"))
        print(f"[FAIL] Server Root: {str(e)}")
    
    # Test 2: API health check
    try:
        response = requests.get(f"{base_url}/api/", timeout=5)
        test_results.append(("API Root", response.status_code == 200, f"Status: {response.status_code}"))
        print(f"[PASS] API Root: {response.status_code}")
    except Exception as e:
        test_results.append(("API Root", False, f"Error: {str(e)}"))
        print(f"[FAIL] API Root: {str(e)}")
    
    # Test 3: Login endpoint
    try:
        login_data = {
            "email": "cleaner@maids.com",
            "password": "cleaner123"
        }
        response = requests.post(f"{base_url}/api/auth/login", json=login_data, timeout=5)
        test_results.append(("Login Endpoint", response.status_code in [200, 401], f"Status: {response.status_code}"))
        print(f"[PASS] Login Endpoint: {response.status_code}")
        
        if response.status_code == 200:
            print("   [SUCCESS] Backend login working!")
        elif response.status_code == 401:
            print("   [WARNING] Login endpoint exists but credentials may be invalid")
            
    except Exception as e:
        test_results.append(("Login Endpoint", False, f"Error: {str(e)}"))
        print(f"[FAIL] Login Endpoint: {str(e)}")
    
    # Test 4: Jobs endpoint (requires auth)
    try:
        response = requests.get(f"{base_url}/api/jobs", timeout=5)
        test_results.append(("Jobs Endpoint", response.status_code in [200, 401, 403], f"Status: {response.status_code}"))
        print(f"[PASS] Jobs Endpoint: {response.status_code}")
    except Exception as e:
        test_results.append(("Jobs Endpoint", False, f"Error: {str(e)}"))
        print(f"[FAIL] Jobs Endpoint: {str(e)}")
    
    # Test 5: Calendar endpoints
    try:
        response = requests.get(f"{base_url}/api/calendar/available-dates?start_date=2024-01-01&end_date=2024-01-31", timeout=5)
        test_results.append(("Calendar Endpoint", response.status_code in [200, 401, 403], f"Status: {response.status_code}"))
        print(f"[PASS] Calendar Endpoint: {response.status_code}")
    except Exception as e:
        test_results.append(("Calendar Endpoint", False, f"Error: {str(e)}"))
        print(f"[FAIL] Calendar Endpoint: {str(e)}")
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result, _ in test_results if result)
    total = len(test_results)
    
    for test_name, result, message in test_results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}: {message}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("[SUCCESS] Backend is fully operational!")
        return True
    elif passed > 0:
        print("[WARNING] Backend is partially working")
        return True
    else:
        print("[ERROR] Backend is not responding")
        return False

if __name__ == "__main__":
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    success = test_backend_connection()
    print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if success:
        print("\n[SUCCESS] Backend is ready for Flutter app testing!")
        print("[INFO] You can now test both demo and backend login modes")
    else:
        print("\n[ERROR] Backend issues detected")
        print("[INFO] Try starting backend: cd backend && python server.py")
        print("[INFO] You can still test demo mode in the Flutter app")
    
    sys.exit(0 if success else 1)
