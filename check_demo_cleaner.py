#!/usr/bin/env python3
"""
Check if demo cleaner account exists in database
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / 'backend' / '.env')

async def check_users():
    """Check if demo cleaner exists"""
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.getenv('DB_NAME', 'maidsofcyfair')
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]

    try:
        print(f"Connecting to: {mongo_url}")
        print(f"Database: {db_name}")

        # Test connection
        await client.admin.command('ping')
        print("Database connection successful!")

        # Check all users
        users = await db.users.find({}).to_list(10)
        print(f"Found {len(users)} users in database")

        # Look for cleaner accounts
        cleaners = await db.users.find({"role": "cleaner"}).to_list(10)
        print(f"Found {len(cleaners)} cleaner accounts")

        for cleaner in cleaners:
            print(f"Cleaner: {cleaner.get('email')} - Role: {cleaner.get('role')}")

        # Check for our demo cleaner specifically
        demo_cleaner = await db.users.find_one({"email": "cleaner@maids.com"})
        if demo_cleaner:
            print("Demo cleaner EXISTS in database!")
            print(f"Email: {demo_cleaner['email']}")
            print(f"Role: {demo_cleaner['role']}")
            print(f"Password hash present: {'password_hash' in demo_cleaner}")
            print(f"Password hash length: {len(demo_cleaner.get('password_hash', ''))}")
        else:
            print("Demo cleaner NOT found in database")
            print("Need to create demo cleaner account")

        # Check database collections
        collections = await db.list_collection_names()
        print(f"Available collections: {collections}")

    except Exception as e:
        print(f"Error connecting to database: {e}")
        print("Make sure MongoDB is running and accessible")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(check_users())
