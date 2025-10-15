#!/usr/bin/env python3
"""
Simple connection test
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def test_connection():
    MONGO_URL = "mongodb+srv://ynitin370:qHdDNJMRw8%40123@maidsofcyfair.rplwzsy.mongodb.net/?retryWrites=true&w=majority&appName=maidsofcyfair"
    DB_NAME = "maidsofcyfair"
    
    print("Testing MongoDB connection...")
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        await db.command('ping')
        print("✅ MongoDB connection successful")
        
        # Test collections
        collections = await db.list_collection_names()
        print(f"📋 Available collections: {collections}")
        
        # Test users collection
        user_count = await db.users.count_documents({})
        print(f"👥 Users in database: {user_count}")
        
        # Test cleaners collection
        cleaner_count = await db.cleaners.count_documents({})
        print(f"🧹 Cleaners in database: {cleaner_count}")
        
        # Test bookings collection
        booking_count = await db.bookings.count_documents({})
        print(f"📅 Bookings in database: {booking_count}")
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {str(e)}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(test_connection())
