#!/usr/bin/env python3
"""
Test MongoDB Connection
======================

This script tests if MongoDB is properly configured and accessible.
Run this after setting up MongoDB to verify the connection works.
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / 'backend' / '.env')

async def test_connection():
    """Test MongoDB connection"""
    print("Testing MongoDB Connection...")
    print("-" * 40)

    # Get connection details
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.getenv('DB_NAME', 'maidsofcyfair')

    print(f"MongoDB URL: {mongo_url}")
    print(f"Database: {db_name}")
    print()

    try:
        # Create client
        client = AsyncIOMotorClient(mongo_url)

        # Test basic connection
        await client.admin.command('ping')
        print("✅ MongoDB connection successful!")

        # Test database access
        db = client[db_name]

        # Check collections
        collections = await db.list_collection_names()
        print(f"✅ Database accessible - Collections: {collections}")

        # Check if users collection exists
        if 'users' in collections:
            users_count = await db.users.count_documents({})
            print(f"✅ Users collection exists - {users_count} users")

            # Check for demo cleaner
            demo_cleaner = await db.users.find_one({"email": "cleaner@maids.com"})
            if demo_cleaner:
                print(f"✅ Demo cleaner found: {demo_cleaner['email']} (role: {demo_cleaner['role']})")
            else:
                print("⚠️  Demo cleaner not found - run: python create_demo_cleaner.py")
        else:
            print("⚠️  Users collection doesn't exist - run: python setup_cloud_mongodb.py")

        # Check if bookings collection exists
        if 'bookings' in collections:
            bookings_count = await db.bookings.count_documents({})
            print(f"✅ Bookings collection exists - {bookings_count} bookings")
        else:
            print("⚠️  Bookings collection doesn't exist")

        print()
        print("🎉 MongoDB is properly configured!")
        print("You can now test the cleaner dashboard.")

    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print()
        print("Troubleshooting steps:")
        print("1. Check if MongoDB is running")
        print("2. Verify connection string in backend/.env")
        print("3. Check firewall/network settings")
        print("4. For Atlas: Verify IP whitelist includes your IP")
        print("5. For local: Run 'net start MongoDB' as administrator")

    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(test_connection())
