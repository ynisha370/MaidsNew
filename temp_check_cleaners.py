#!/usr/bin/env python3
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check_cleaners():
    client = AsyncIOMotorClient("mongodb+srv://ynitin370:qHdDNJMRw8%40123@maidsofcyfair.rplwzsy.mongodb.net/?retryWrites=true&w=majority&appName=maidsofcyfair")
    db = client["maidsofcyfair"]

    print("🔍 Checking cleaners in database...")

    # Get all cleaners
    cleaners = await db.cleaners.find().to_list(1000)
    print("Total cleaners in database: {}".format(len(cleaners)))

    if cleaners:
        print("\n🧹 Cleaners found:")
        for cleaner in cleaners:
            print("  - Name: {} {}".format(cleaner.get('first_name', 'N/A'), cleaner.get('last_name', 'N/A')))
            print("    Email: {}".format(cleaner.get('email', 'N/A')))
            print("    ID: {}".format(cleaner.get('id', 'N/A')))
            print("    Active: {}".format(cleaner.get('is_active', 'N/A')))
            print("    Calendar Enabled: {}".format(cleaner.get('calendar_integration_enabled', 'N/A')))
            print("    Google Calendar ID: {}".format(cleaner.get('google_calendar_id', 'N/A')))
            print("    Total Jobs: {}".format(cleaner.get('total_jobs', 'N/A')))
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
