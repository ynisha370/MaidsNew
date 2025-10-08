#!/usr/bin/env python3
"""
Check cleaners in the database
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check_cleaners():
    client = AsyncIOMotorClient("mongodb+srv://ynitin370:qHdDNJMRw8%40123@maidsofcyfair.rplwzsy.mongodb.net/?retryWrites=true&w=majority&appName=maidsofcyfair")
    db = client["maidsofcyfair"]

    print("🔍 Checking cleaners in database...")

    # Get all cleaners
    cleaners = await db.cleaners.find().to_list(1000)
    print(f"Total cleaners in database: {len(cleaners)}")

    if cleaners:
        print("\n🧹 Cleaners found:")
        for cleaner in cleaners:
            print(f"  - Name: {cleaner.get('first_name', 'N/A')} {cleaner.get('last_name', 'N/A')}")
            print(f"    Email: {cleaner.get('email', 'N/A')}")
            print(f"    ID: {cleaner.get('id', 'N/A')}")
            print(f"    Active: {cleaner.get('is_active', 'N/A')}")
            print(f"    Calendar Enabled: {cleaner.get('calendar_integration_enabled', 'N/A')}")
            print(f"    Google Calendar ID: {cleaner.get('google_calendar_id', 'N/A')}")
            print(f"    Total Jobs: {cleaner.get('total_jobs', 'N/A')}")
            if cleaner.get('google_calendar_credentials'):
                print("    ✅ Has Google Calendar credentials")
            else:
                print("    ❌ No Google Calendar credentials")
            print()
    else:
        print("❌ No cleaners found in database")

    client.close()

if __name__ == "__main__":
    asyncio.run(check_cleaners())
