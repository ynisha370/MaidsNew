#!/usr/bin/env python3
"""
Test script to fix cleaner showing as busy
"""

import asyncio
import requests
from motor.motor_asyncio import AsyncIOMotorClient
import uuid
from datetime import datetime, timezone

async def test_cleaner_availability():
    print("Testing Cleaner Availability Fix...")

    # Connect to MongoDB
    client = AsyncIOMotorClient("mongodb+srv://ynitin370:qHdDNJMRw8%40123@maidsofcyfair.rplwzsy.mongodb.net/?retryWrites=true&w=majority&appName=maidsofcyfair")
    db = client["maidsofcyfair"]

    try:
        # 1. Check if test cleaner exists and is properly configured
        print("\n1. Checking test cleaner...")
        test_cleaner = await db.cleaners.find_one({"email": "testcleaner@maids.com"})

        if test_cleaner:
            print(f"Test cleaner found: {test_cleaner['first_name']} {test_cleaner['last_name']}")
            print(f"   Calendar enabled: {test_cleaner.get('calendar_integration_enabled', False)}")
            print(f"   Has credentials: {'google_calendar_credentials' in test_cleaner}")

            if test_cleaner.get('calendar_integration_enabled'):
                print("Cleaner shows as 'Connected' - calendar integration is enabled")
            else:
                print("Cleaner shows as 'No Calendar' - calendar integration not enabled")
        else:
            print("Test cleaner not found")

        # 2. Check availability summary
        print("\n2. Testing availability summary...")
        try:
            # Start backend server first
            import subprocess
            import time

            print("Starting backend server...")
            backend_process = subprocess.Popen([
                "python", "-m", "uvicorn", "server:app",
                "--host", "0.0.0.0", "--port", "8002"
            ], cwd="backend")

            time.sleep(5)  # Wait for server to start

            try:
                today = datetime.now().strftime("%Y-%m-%d")
                response = requests.get(f"http://localhost:8002/api/admin/calendar/availability-summary?date={today}")

                if response.status_code == 200:
                    data = response.json()
                    print(f"Availability summary working - Found {len(data.get('cleaners', []))} cleaners")

                    # Find our test cleaner
                    test_cleaner_data = None
                    for cleaner in data.get('cleaners', []):
                        if cleaner['cleaner_id'] == test_cleaner['id']:
                            test_cleaner_data = cleaner
                            break

                    if test_cleaner_data:
                        print(f"Test cleaner found in availability: {test_cleaner_data['cleaner_name']}")
                        print(f"   Calendar enabled: {test_cleaner_data['calendar_enabled']}")

                        # Check time slots
                        available_slots = 0
                        for slot, slot_data in test_cleaner_data.get('slots', {}).items():
                            if slot_data.get('available', False):
                                available_slots += 1
                                print(f"   Slot {slot}: Available")
                            else:
                                print(f"   Slot {slot}: Busy")

                        print(f"   Available slots: {available_slots}/{len(test_cleaner_data.get('slots', {}))}")

                        if available_slots > 0:
                            print("Test cleaner has available slots - should show as available")
                        else:
                            print("Test cleaner has no available slots - showing as busy")
                    else:
                        print("Test cleaner not found in availability summary")
                else:
                    print(f"Availability summary failed: {response.status_code} - {response.text}")

            finally:
                print("Stopping backend server...")
                backend_process.terminate()
                backend_process.wait()

        except Exception as e:
            print(f"Availability test error: {e}")

        # 3. Check if any bookings exist for the test cleaner
        print("\n3. Checking existing bookings for test cleaner...")
        if test_cleaner:
            bookings = await db.bookings.find({
                "cleaner_id": test_cleaner["id"]
            }).to_list(10)

            print(f"Found {len(bookings)} bookings for test cleaner")
            for booking in bookings:
                print(f"   - {booking['booking_date']} {booking['time_slot']}: {booking.get('status', 'unknown')}")

        print("\nTest completed!")

    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(test_cleaner_availability())
