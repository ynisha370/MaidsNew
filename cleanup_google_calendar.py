#!/usr/bin/env python3
"""
Database Cleanup Script for Google Calendar Integration Removal
Removes all Google Calendar-related fields from the database
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / 'backend/.env')

# MongoDB connection
mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
db_name = os.getenv("DB_NAME", "maidsofcyfair")

# Handle special characters in password for cloud MongoDB
if "qHdDNJMRw8@123" in mongo_url:
    mongo_url = mongo_url.replace("qHdDNJMRw8@123", "qHdDNJMRw8%40123")

print("="*70)
print("GOOGLE CALENDAR DATA CLEANUP")
print("="*70)
print(f"\nConnecting to database: {db_name}")
print(f"MongoDB URL: {mongo_url[:50]}...")

async def cleanup_database():
    """Remove all Google Calendar related fields from the database"""
    
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        print("\n✅ Successfully connected to MongoDB\n")
        
        # 1. Remove Google Calendar fields from cleaners collection
        print("📋 Cleaning cleaners collection...")
        cleaners_result = await db.cleaners.update_many(
            {},
            {
                "$unset": {
                    "google_calendar_credentials": "",
                    "google_calendar_id": "",
                    "calendar_integration_enabled": ""
                }
            }
        )
        print(f"   ✅ Updated {cleaners_result.modified_count} cleaner records")
        
        # 2. Remove calendar_event_id from bookings collection
        print("\n📋 Cleaning bookings collection...")
        bookings_result = await db.bookings.update_many(
            {},
            {
                "$unset": {
                    "calendar_event_id": ""
                }
            }
        )
        print(f"   ✅ Updated {bookings_result.modified_count} booking records")
        
        # 3. Show summary of remaining data
        print("\n" + "="*70)
        print("CLEANUP SUMMARY")
        print("="*70)
        
        total_cleaners = await db.cleaners.count_documents({})
        print(f"\n✅ Total cleaners in database: {total_cleaners}")
        
        cleaners_with_gcal = await db.cleaners.count_documents({
            "$or": [
                {"google_calendar_credentials": {"$exists": True}},
                {"google_calendar_id": {"$exists": True}},
                {"calendar_integration_enabled": {"$exists": True}}
            ]
        })
        print(f"   Cleaners still with Google Calendar fields: {cleaners_with_gcal}")
        
        total_bookings = await db.bookings.count_documents({})
        print(f"\n✅ Total bookings in database: {total_bookings}")
        
        bookings_with_event_id = await db.bookings.count_documents({
            "calendar_event_id": {"$exists": True}
        })
        print(f"   Bookings still with calendar_event_id: {bookings_with_event_id}")
        
        # 4. Show cleaner_availability records (these are kept - part of custom calendar)
        availability_count = await db.cleaner_availability.count_documents({})
        print(f"\n✅ Cleaner availability records (custom calendar): {availability_count}")
        print("   (These records are kept as part of the custom calendar system)")
        
        print("\n" + "="*70)
        if cleaners_with_gcal == 0 and bookings_with_event_id == 0:
            print("✅ CLEANUP SUCCESSFUL - All Google Calendar data removed!")
        else:
            print("⚠️  WARNING - Some Google Calendar data still exists")
        print("="*70)
        
        # Close connection
        client.close()
        
    except Exception as e:
        print(f"\n❌ Error during cleanup: {str(e)}")
        raise

async def main():
    """Main function"""
    print("\n⚠️  This script will remove all Google Calendar related data from the database.")
    print("   This includes:")
    print("   - google_calendar_credentials from cleaners")
    print("   - google_calendar_id from cleaners")
    print("   - calendar_integration_enabled from cleaners")
    print("   - calendar_event_id from bookings")
    print("\n   The custom calendar availability data (cleaner_availability) will be preserved.")
    
    response = input("\n🔴 Do you want to proceed? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        await cleanup_database()
    else:
        print("\n❌ Cleanup cancelled by user")

if __name__ == "__main__":
    asyncio.run(main())

