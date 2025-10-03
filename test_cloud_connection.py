#!/usr/bin/env python3
"""
Test Cloud MongoDB Connection
This script tests the connection to your cloud MongoDB database.
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / 'backend' / '.env')

async def test_cloud_connection():
    """Test the cloud MongoDB connection"""
    
    # Get connection details
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    db_name = os.getenv("DB_NAME", "maidsofcyfair")
    
    print(f"🔗 Testing connection to: {mongo_url}")
    print(f"📊 Database: {db_name}")
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    try:
        # Test basic connection
        print("\n1️⃣ Testing basic connection...")
        await client.admin.command('ping')
        print("✅ Connection successful!")
        
        # Test database access
        print("\n2️⃣ Testing database access...")
        collections = await db.list_collection_names()
        print(f"✅ Found {len(collections)} collections: {collections}")
        
        # Test each collection
        print("\n3️⃣ Testing collections...")
        
        # Users collection
        users_count = await db.users.count_documents({})
        print(f"   👥 Users: {users_count}")
        
        # Services collection
        services_count = await db.services.count_documents({})
        print(f"   📋 Services: {services_count}")
        
        # Time slots collection
        time_slots_count = await db.time_slots.count_documents({})
        print(f"   ⏰ Time Slots: {time_slots_count}")
        
        # Bookings collection
        bookings_count = await db.bookings.count_documents({})
        print(f"   📅 Bookings: {bookings_count}")
        
        # Cleaners collection
        cleaners_count = await db.cleaners.count_documents({})
        print(f"   🧹 Cleaners: {cleaners_count}")
        
        # Promo codes collection
        promo_codes_count = await db.promo_codes.count_documents({})
        print(f"   🎫 Promo Codes: {promo_codes_count}")
        
        # Test reading some data
        print("\n4️⃣ Testing data access...")
        
        if services_count > 0:
            services = await db.services.find().limit(3).to_list(3)
            print(f"   📋 Sample services: {[s['name'] for s in services]}")
        
        if cleaners_count > 0:
            cleaners = await db.cleaners.find().limit(3).to_list(3)
            print(f"   🧹 Sample cleaners: {[c['name'] for c in cleaners]}")
        
        # Test writing data
        print("\n5️⃣ Testing write operations...")
        test_doc = {
            "test": True,
            "timestamp": "2024-01-01T00:00:00Z",
            "message": "Cloud MongoDB connection test"
        }
        
        result = await db.test_collection.insert_one(test_doc)
        print(f"   ✅ Write test successful: {result.inserted_id}")
        
        # Clean up test document
        await db.test_collection.delete_one({"_id": result.inserted_id})
        print("   🧹 Test document cleaned up")
        
        # Test connection performance
        print("\n6️⃣ Testing connection performance...")
        import time
        
        start_time = time.time()
        for _ in range(10):
            await db.services.find().limit(1).to_list(1)
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 10
        print(f"   ⚡ Average query time: {avg_time:.3f}s")
        
        if avg_time < 0.1:
            print("   🚀 Excellent performance!")
        elif avg_time < 0.5:
            print("   ✅ Good performance")
        else:
            print("   ⚠️  Performance could be better")
        
        print("\n🎉 Cloud MongoDB connection test completed successfully!")
        print("\n📝 Your database is ready to use!")
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("   1. Check your MONGO_URL in the .env file")
        print("   2. Ensure your cloud MongoDB is accessible")
        print("   3. Verify your IP is whitelisted (if required)")
        print("   4. Check your username/password")
        raise
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(test_cloud_connection())
