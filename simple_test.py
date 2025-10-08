#!/usr/bin/env python3
import requests
from datetime import datetime

def test_calendar_endpoints():
    print("Testing Calendar Endpoints...")

    base_url = "http://localhost:8001/api"

    # Test 1: Get unassigned jobs
    try:
        print("\n1. Testing unassigned jobs endpoint...")
        response = requests.get(f"{base_url}/admin/calendar/unassigned-jobs")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            jobs = data.get('unassigned_jobs', [])
            print(f"✅ Found {len(jobs)} unassigned jobs")
            if jobs:
                print(f"   Sample job: {jobs[0]['id'][:8]}... - {jobs[0]['house_size']}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Connection error: {e}")

    # Test 2: Get availability summary
    try:
        print("\n2. Testing availability summary endpoint...")
        today = datetime.now().strftime("%Y-%m-%d")
        response = requests.get(f"{base_url}/admin/calendar/availability-summary?date={today}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            cleaners = data.get('cleaners', [])
            print(f"✅ Found {len(cleaners)} cleaners in availability")
            if cleaners:
                print(f"   Sample cleaner: {cleaners[0]['cleaner_name']}")
                print(f"   Calendar enabled: {cleaners[0]['calendar_enabled']}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    test_calendar_endpoints()
