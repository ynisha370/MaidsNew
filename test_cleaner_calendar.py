#!/usr/bin/env python3
import asyncio
import requests
from motor.motor_asyncio import AsyncIOMotorClient
import uuid
from datetime import datetime, timezone

async def test_cleaner_calendar():
    print("🧪 Testing Cleaner Calendar Integration...")

    # Connect to MongoDB
    client = AsyncIOMotorClient("mongodb+srv://ynitin370:qHdDNJMRw8%40123@maidsofcyfair.rplwzsy.mongodb.net/?retryWrites=true&w=majority&appName=maidsofcyfair")
    db = client["maidsofcyfair"]

    try:
        # 1. Create or get demo cleaner with calendar integration
        print("\n1. Setting up demo cleaner with calendar integration...")

        cleaner_email = "testcleaner@maids.com"
        existing_cleaner = await db.cleaners.find_one({"email": cleaner_email})

        if existing_cleaner:
            print("✅ Demo cleaner already exists")
            cleaner_id = existing_cleaner["id"]
        else:
            cleaner_data = {
                "id": str(uuid.uuid4()),
                "email": cleaner_email,
                "first_name": "Test",
                "last_name": "Cleaner",
                "phone": "(281) 555-1234",
                "is_active": True,
                "rating": 4.5,
                "total_jobs": 10,
                "google_calendar_credentials": {
                    "type": "authorized_user",
                    "client_id": "test-client-id",
                    "client_secret": "test-client-secret",
                    "refresh_token": "test-refresh-token"
                },
                "google_calendar_id": "primary",
                "calendar_integration_enabled": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            }

            await db.cleaners.insert_one(cleaner_data)
            cleaner_id = cleaner_data["id"]
            print("✅ Demo cleaner created with calendar integration")

        # 2. Test calendar availability endpoint
        print("\n2. Testing calendar availability endpoint...")

        # Start backend server first
        import subprocess
        import time

        print("Starting backend server...")
        backend_process = subprocess.Popen([
            "python", "-m", "uvicorn", "server:app",
            "--host", "0.0.0.0", "--port", "8001"
        ], cwd="backend")

        time.sleep(3)  # Wait for server to start

        try:
            # Test availability endpoint
            today = datetime.now().strftime("%Y-%m-%d")
            response = requests.get(f"http://localhost:8001/api/admin/calendar/availability-summary?date={today}")

            if response.status_code == 200:
                data = response.json()
                print(f"✅ Availability endpoint working - Found {len(data.get('cleaners', []))} cleaners")

                # Check if our test cleaner is in the response
                test_cleaner = next((c for c in data.get('cleaners', []) if c['cleaner_id'] == cleaner_id), None)
                if test_cleaner:
                    print(f"✅ Test cleaner found in availability response")
                    print(f"   - Name: {test_cleaner['cleaner_name']}")
                    print(f"   - Calendar Enabled: {test_cleaner['calendar_enabled']}")
                    print(f"   - Available Slots: {len(test_cleaner.get('slots', {}))}")
                else:
                    print("❌ Test cleaner not found in availability response")
            else:
                print(f"❌ Availability endpoint failed: {response.status_code} - {response.text}")

            # 3. Test unassigned jobs endpoint
            print("\n3. Testing unassigned jobs endpoint...")
            response = requests.get("http://localhost:8001/api/admin/calendar/unassigned-jobs")

            if response.status_code == 200:
                data = response.json()
                unassigned_jobs = data.get('unassigned_jobs', [])
                print(f"✅ Unassigned jobs endpoint working - Found {len(unassigned_jobs)} jobs")

                if unassigned_jobs:
                    print(f"📋 First unassigned job: {unassigned_jobs[0]['id'][:8]}... - {unassigned_jobs[0]['house_size']}")
            else:
                print(f"❌ Unassigned jobs endpoint failed: {response.status_code} - {response.text}")

        finally:
            print("\nStopping backend server...")
            backend_process.terminate()
            backend_process.wait()

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

    print("\n🎉 Calendar integration test completed!")

if __name__ == "__main__":
    asyncio.run(test_cleaner_calendar())
