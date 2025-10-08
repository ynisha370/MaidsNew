#!/usr/bin/env python3
import requests
import os
import json
from datetime import datetime

# Set up backend URL
BACKEND_URL = "http://localhost:8000"
API_BASE = f"{BACKEND_URL}/api"

def test_calendar_endpoints():
    print("Testing Calendar Endpoints...")

    # Test 1: Get unassigned jobs
    try:
        print("\n1. Testing /admin/calendar/unassigned-jobs")
        response = requests.get(f"{API_BASE}/admin/calendar/unassigned-jobs")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data.get('unassigned_jobs', []))} unassigned jobs")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

    # Test 2: Get availability summary
    try:
        print("\n2. Testing /admin/calendar/availability-summary")
        date = datetime.now().strftime("%Y-%m-%d")
        response = requests.get(f"{API_BASE}/admin/calendar/availability-summary?date={date}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data.get('cleaners', []))} cleaners")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

    print("\nTest completed!")

if __name__ == "__main__":
    test_calendar_endpoints()
