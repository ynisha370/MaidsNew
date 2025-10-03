#!/usr/bin/env python3
"""
Setup Cloud MongoDB Database
This script initializes the cloud MongoDB database with the required collections and initial data.
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import uuid
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / 'backend' / '.env')

async def setup_cloud_mongodb():
    """Initialize cloud MongoDB with required collections and data"""
    
    # Get connection details
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    db_name = os.getenv("DB_NAME", "maidsofcyfair")
    
    print(f"🔗 Connecting to MongoDB: {mongo_url}")
    print(f"📊 Database: {db_name}")
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    try:
        # Test connection
        await client.admin.command('ping')
        print("✅ Successfully connected to MongoDB!")
        
        # 1. Create Services Collection
        print("\n📋 Setting up services collection...")
        services_data = [
            {
                "id": "standard_cleaning",
                "name": "Standard Cleaning",
                "description": "Basic house cleaning service",
                "base_price": 120.0,
                "is_a_la_carte": False,
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "id": "deep_cleaning",
                "name": "Deep Cleaning",
                "description": "Thorough deep cleaning service",
                "base_price": 200.0,
                "is_a_la_carte": False,
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "id": "move_in_out",
                "name": "Move In/Out Cleaning",
                "description": "Comprehensive cleaning for moving",
                "base_price": 300.0,
                "is_a_la_carte": False,
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "id": "window_cleaning",
                "name": "Window Cleaning",
                "description": "Professional window cleaning",
                "base_price": 50.0,
                "is_a_la_carte": True,
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "id": "refrigerator_cleaning",
                "name": "Refrigerator Cleaning",
                "description": "Deep clean inside and outside of refrigerator",
                "base_price": 40.0,
                "is_a_la_carte": True,
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "id": "oven_cleaning",
                "name": "Oven Cleaning",
                "description": "Deep clean oven and stovetop",
                "base_price": 35.0,
                "is_a_la_carte": True,
                "created_at": datetime.utcnow().isoformat()
            }
        ]
        
        # Clear existing services and insert new ones
        await db.services.delete_many({})
        await db.services.insert_many(services_data)
        print(f"✅ Created {len(services_data)} services")
        
        # 2. Create Time Slots Collection
        print("\n⏰ Setting up time slots collection...")
        time_slots = []
        base_date = datetime.now().date()
        
        # Create time slots for the next 30 days
        for day_offset in range(30):
            current_date = base_date + timedelta(days=day_offset)
            date_str = current_date.strftime("%Y-%m-%d")
            
            # Available time slots
            slots = [
                "08:00-10:00", "10:00-12:00", "12:00-14:00", 
                "14:00-16:00", "16:00-18:00", "18:00-20:00"
            ]
            
            for slot in slots:
                time_slots.append({
                    "date": date_str,
                    "time_slot": slot,
                    "is_available": True,
                    "created_at": datetime.utcnow().isoformat()
                })
        
        # Clear existing time slots and insert new ones
        await db.time_slots.delete_many({})
        await db.time_slots.insert_many(time_slots)
        print(f"✅ Created {len(time_slots)} time slots")
        
        # 3. Create Promo Codes Collection (empty initially)
        print("\n🎫 Setting up promo codes collection...")
        await db.promo_codes.delete_many({})
        print("✅ Promo codes collection ready")
        
        # 4. Create Users Collection (empty initially)
        print("\n👥 Setting up users collection...")
        await db.users.delete_many({})
        print("✅ Users collection ready")
        
        # 5. Create Bookings Collection (empty initially)
        print("\n📅 Setting up bookings collection...")
        await db.bookings.delete_many({})
        print("✅ Bookings collection ready")
        
        # 6. Create Cleaners Collection
        print("\n🧹 Setting up cleaners collection...")
        cleaners_data = [
            {
                "id": str(uuid.uuid4()),
                "name": "Maria Rodriguez",
                "email": "maria@maidsofcyfair.com",
                "phone": "+1-555-0101",
                "specialties": ["standard_cleaning", "deep_cleaning"],
                "rating": 4.9,
                "is_available": True,
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Ana Silva",
                "email": "ana@maidsofcyfair.com",
                "phone": "+1-555-0102",
                "specialties": ["standard_cleaning", "window_cleaning"],
                "rating": 4.8,
                "is_available": True,
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Carmen Lopez",
                "email": "carmen@maidsofcyfair.com",
                "phone": "+1-555-0103",
                "specialties": ["deep_cleaning", "move_in_out"],
                "rating": 5.0,
                "is_available": True,
                "created_at": datetime.utcnow().isoformat()
            }
        ]
        
        await db.cleaners.delete_many({})
        await db.cleaners.insert_many(cleaners_data)
        print(f"✅ Created {len(cleaners_data)} cleaners")
        
        # 7. Create Indexes for better performance
        print("\n🔍 Creating database indexes...")
        
        # Users indexes
        await db.users.create_index("email", unique=True)
        await db.users.create_index("id", unique=True)
        
        # Bookings indexes
        await db.bookings.create_index("user_id")
        await db.bookings.create_index("booking_date")
        await db.bookings.create_index("status")
        await db.bookings.create_index("id", unique=True)
        
        # Services indexes
        await db.services.create_index("id", unique=True)
        await db.services.create_index("is_a_la_carte")
        
        # Time slots indexes
        await db.time_slots.create_index([("date", 1), ("time_slot", 1)])
        await db.time_slots.create_index("is_available")
        
        # Promo codes indexes
        await db.promo_codes.create_index("code", unique=True)
        await db.promo_codes.create_index("id", unique=True)
        await db.promo_codes.create_index("is_active")
        
        # Cleaners indexes
        await db.cleaners.create_index("id", unique=True)
        await db.cleaners.create_index("is_available")
        
        print("✅ Database indexes created")
        
        # 8. Create a test user for development
        print("\n🧪 Creating test user...")
        test_user = {
            "id": str(uuid.uuid4()),
            "email": "test@maidsofcyfair.com",
            "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8Q8Q8Q8",  # password: test123
            "first_name": "Test",
            "last_name": "User",
            "phone": "+1-555-0000",
            "address": {
                "street": "123 Test Street",
                "city": "Houston",
                "state": "TX",
                "zip_code": "77433"
            },
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        await db.users.insert_one(test_user)
        print(f"✅ Test user created: {test_user['email']}")
        
        # 9. Display database statistics
        print("\n📊 Database Statistics:")
        print(f"   Users: {await db.users.count_documents({})}")
        print(f"   Services: {await db.services.count_documents({})}")
        print(f"   Time Slots: {await db.time_slots.count_documents({})}")
        print(f"   Cleaners: {await db.cleaners.count_documents({})}")
        print(f"   Bookings: {await db.bookings.count_documents({})}")
        print(f"   Promo Codes: {await db.promo_codes.count_documents({})}")
        
        print("\n🎉 Cloud MongoDB setup completed successfully!")
        print("\n📝 Next steps:")
        print("   1. Update your .env file with the cloud MongoDB connection string")
        print("   2. Test the connection using: python test_cloud_connection.py")
        print("   3. Start your application: python backend/server.py")
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        raise
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(setup_cloud_mongodb())
