"""
Database Seeding Script
Populates database with test cleaners, users, and sample data
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
import uuid

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
import bcrypt

# Load environment
load_dotenv(Path(__file__).parent / 'backend' / '.env')

# MongoDB connection
mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
db_name = os.getenv("DB_NAME", "maidsofcyfair")

# Fix password encoding in URL
if "qHdDNJMRw8@123" in mongo_url:
    mongo_url = mongo_url.replace("qHdDNJMRw8@123", "qHdDNJMRw8%40123")

client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

async def seed_users():
    """Create test users"""
    print("\n📝 Seeding Users...")
    
    users = [
        {
            "id": str(uuid.uuid4()),
            "email": "admin@maids.com",
            "first_name": "Admin",
            "last_name": "User",
            "phone": "+1234567890",
            "password_hash": hash_password("admin123"),
            "role": "admin",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "email": "customer1@test.com",
            "first_name": "John",
            "last_name": "Customer",
            "phone": "+1234567891",
            "password_hash": hash_password("password123"),
            "role": "customer",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "email": "customer2@test.com",
            "first_name": "Sarah",
            "last_name": "Johnson",
            "phone": "+1234567892",
            "password_hash": hash_password("password123"),
            "role": "customer",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    for user in users:
        existing = await db.users.find_one({"email": user["email"]})
        if existing:
            print(f"  ⏭️  User {user['email']} already exists")
        else:
            await db.users.insert_one(user)
            print(f"  ✓ Created user: {user['email']} ({user['role']})")
    
    return users

async def seed_cleaners():
    """Create test cleaners (some approved, some pending)"""
    print("\n🧹 Seeding Cleaners...")
    
    # First, create user accounts for cleaners
    cleaner_users = [
        {
            "id": str(uuid.uuid4()),
            "email": "cleaner1@maids.com",
            "first_name": "Maria",
            "last_name": "Garcia",
            "phone": "+1234567893",
            "password_hash": hash_password("cleaner123"),
            "role": "cleaner",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "email": "cleaner2@maids.com",
            "first_name": "James",
            "last_name": "Wilson",
            "phone": "+1234567894",
            "password_hash": hash_password("cleaner123"),
            "role": "cleaner",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "email": "cleaner3@maids.com",
            "first_name": "Lisa",
            "last_name": "Chen",
            "phone": "+1234567895",
            "password_hash": hash_password("cleaner123"),
            "role": "cleaner",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "email": "pending1@maids.com",
            "first_name": "Mike",
            "last_name": "Brown",
            "phone": "+1234567896",
            "password_hash": hash_password("cleaner123"),
            "role": "cleaner",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "email": "pending2@maids.com",
            "first_name": "Emily",
            "last_name": "Davis",
            "phone": "+1234567897",
            "password_hash": hash_password("cleaner123"),
            "role": "cleaner",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    # Create user accounts
    for user in cleaner_users:
        existing = await db.users.find_one({"email": user["email"]})
        if not existing:
            await db.users.insert_one(user)
            print(f"  ✓ Created user account: {user['email']}")
    
    # Create cleaner profiles
    cleaners = [
        {
            "id": str(uuid.uuid4()),
            "email": "cleaner1@maids.com",
            "first_name": "Maria",
            "last_name": "Garcia",
            "phone": "+1234567893",
            "is_active": True,
            "is_approved": True,
            "approved_at": datetime.utcnow(),
            "approved_by": "admin",
            "rating": 4.8,
            "total_jobs": 45,
            "google_calendar_credentials": None,
            "google_calendar_id": "primary",
            "calendar_integration_enabled": False,
            "created_at": datetime.utcnow() - timedelta(days=60)
        },
        {
            "id": str(uuid.uuid4()),
            "email": "cleaner2@maids.com",
            "first_name": "James",
            "last_name": "Wilson",
            "phone": "+1234567894",
            "is_active": True,
            "is_approved": True,
            "approved_at": datetime.utcnow(),
            "approved_by": "admin",
            "rating": 4.9,
            "total_jobs": 38,
            "google_calendar_credentials": None,
            "google_calendar_id": "primary",
            "calendar_integration_enabled": False,
            "created_at": datetime.utcnow() - timedelta(days=45)
        },
        {
            "id": str(uuid.uuid4()),
            "email": "cleaner3@maids.com",
            "first_name": "Lisa",
            "last_name": "Chen",
            "phone": "+1234567895",
            "is_active": True,
            "is_approved": True,
            "approved_at": datetime.utcnow(),
            "approved_by": "admin",
            "rating": 5.0,
            "total_jobs": 52,
            "google_calendar_credentials": None,
            "google_calendar_id": "primary",
            "calendar_integration_enabled": False,
            "created_at": datetime.utcnow() - timedelta(days=90)
        },
        {
            "id": str(uuid.uuid4()),
            "email": "pending1@maids.com",
            "first_name": "Mike",
            "last_name": "Brown",
            "phone": "+1234567896",
            "is_active": True,
            "is_approved": False,  # PENDING
            "approved_at": None,
            "approved_by": None,
            "rating": 5.0,
            "total_jobs": 0,
            "google_calendar_credentials": None,
            "google_calendar_id": "primary",
            "calendar_integration_enabled": False,
            "created_at": datetime.utcnow() - timedelta(days=2)
        },
        {
            "id": str(uuid.uuid4()),
            "email": "pending2@maids.com",
            "first_name": "Emily",
            "last_name": "Davis",
            "phone": "+1234567897",
            "is_active": True,
            "is_approved": False,  # PENDING
            "approved_at": None,
            "approved_by": None,
            "rating": 5.0,
            "total_jobs": 0,
            "google_calendar_credentials": None,
            "google_calendar_id": "primary",
            "calendar_integration_enabled": False,
            "created_at": datetime.utcnow() - timedelta(days=1)
        }
    ]
    
    for cleaner in cleaners:
        existing = await db.cleaners.find_one({"email": cleaner["email"]})
        if existing:
            print(f"  ⏭️  Cleaner {cleaner['email']} already exists")
        else:
            await db.cleaners.insert_one(cleaner)
            status = "APPROVED" if cleaner["is_approved"] else "PENDING"
            print(f"  ✓ Created cleaner: {cleaner['first_name']} {cleaner['last_name']} - {status}")
    
    return cleaners

async def seed_cleaner_availability():
    """Create availability slots for approved cleaners"""
    print("\n📅 Seeding Cleaner Availability...")
    
    # Get approved cleaners
    approved_cleaners = await db.cleaners.find({"is_approved": True}).to_list(100)
    
    time_slots = [
        "08:00-10:00",
        "10:00-12:00",
        "12:00-14:00",
        "14:00-16:00",
        "16:00-18:00"
    ]
    
    count = 0
    for cleaner in approved_cleaners:
        cleaner_id = cleaner["id"]
        
        # Create availability for next 30 days
        for day_offset in range(30):
            date = datetime.now() + timedelta(days=day_offset)
            date_str = date.strftime("%Y-%m-%d")
            
            for time_slot in time_slots:
                existing = await db.cleaner_availability.find_one({
                    "cleaner_id": cleaner_id,
                    "date": date_str,
                    "time_slot": time_slot
                })
                
                if not existing:
                    availability = {
                        "id": str(uuid.uuid4()),
                        "cleaner_id": cleaner_id,
                        "date": date_str,
                        "time_slot": time_slot,
                        "is_available": True,
                        "is_booked": False,
                        "booking_id": None,
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                    await db.cleaner_availability.insert_one(availability)
                    count += 1
    
    print(f"  ✓ Created {count} availability slots")

async def seed_time_slot_availability():
    """Create time slot availability for bookings"""
    print("\n⏰ Seeding Time Slot Availability...")
    
    time_slots = [
        "08:00-10:00",
        "10:00-12:00",
        "12:00-14:00",
        "14:00-16:00",
        "16:00-18:00"
    ]
    
    count = 0
    # Create for next 30 days
    for day_offset in range(30):
        date = datetime.now() + timedelta(days=day_offset)
        date_str = date.strftime("%Y-%m-%d")
        
        for time_slot in time_slots:
            existing = await db.time_slot_availability.find_one({
                "date": date_str,
                "time_slot": time_slot
            })
            
            if not existing:
                slot_data = {
                    "id": str(uuid.uuid4()),
                    "date": date_str,
                    "time_slot": time_slot,
                    "total_capacity": 5,
                    "booked_count": 0,
                    "is_blocked": False,
                    "blocked_reason": None,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                await db.time_slot_availability.insert_one(slot_data)
                count += 1
    
    print(f"  ✓ Created {count} time slot availability records")

async def main():
    """Main seeding function"""
    print("=" * 60)
    print("DATABASE SEEDING SCRIPT")
    print("=" * 60)
    
    try:
        # Test connection
        await db.command('ping')
        print("\n✓ Connected to MongoDB successfully")
        
        # Seed data
        await seed_users()
        await seed_cleaners()
        await seed_cleaner_availability()
        await seed_time_slot_availability()
        
        # Summary
        print("\n" + "=" * 60)
        print("SEEDING COMPLETE!")
        print("=" * 60)
        
        # Count records
        user_count = await db.users.count_documents({})
        cleaner_count = await db.cleaners.count_documents({})
        approved_count = await db.cleaners.count_documents({"is_approved": True})
        pending_count = await db.cleaners.count_documents({"is_approved": False})
        availability_count = await db.cleaner_availability.count_documents({})
        slot_count = await db.time_slot_availability.count_documents({})
        
        print(f"\n📊 Database Summary:")
        print(f"  Users: {user_count}")
        print(f"  Cleaners: {cleaner_count} (Approved: {approved_count}, Pending: {pending_count})")
        print(f"  Cleaner Availability Slots: {availability_count}")
        print(f"  Time Slot Availability: {slot_count}")
        
        print(f"\n🔑 Test Credentials:")
        print(f"  Admin:")
        print(f"    Email: admin@maids.com")
        print(f"    Password: admin123")
        print(f"\n  Approved Cleaners:")
        print(f"    Email: cleaner1@maids.com (Maria Garcia)")
        print(f"    Email: cleaner2@maids.com (James Wilson)")
        print(f"    Email: cleaner3@maids.com (Lisa Chen)")
        print(f"    Password: cleaner123")
        print(f"\n  Pending Cleaners:")
        print(f"    Email: pending1@maids.com (Mike Brown)")
        print(f"    Email: pending2@maids.com (Emily Davis)")
        print(f"    Password: cleaner123 (will be rejected until approved)")
        print(f"\n  Customers:")
        print(f"    Email: customer1@test.com")
        print(f"    Email: customer2@test.com")
        print(f"    Password: password123")
        
        print("\n✅ Ready for testing!")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())

