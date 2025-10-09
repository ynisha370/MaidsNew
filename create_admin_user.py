#!/usr/bin/env python3
"""
Create an admin user for testing
"""
import asyncio
import os
import bcrypt
import uuid
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

# Database connection
MONGODB_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DB_NAME", "maidsofcyfair")

# Fix MongoDB URL if it has special characters
if "qHdDNJMRw8@123" in MONGODB_URL:
    MONGODB_URL = MONGODB_URL.replace("qHdDNJMRw8@123", "qHdDNJMRw8%40123")

async def create_admin_user():
    """Create an admin user"""
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    try:
        # Check if admin user exists
        existing_admin = await db.users.find_one({"email": "admin@maidsofcyfair.com"})
        
        if existing_admin:
            print(f"✅ Admin user already exists: {existing_admin['email']}")
            print(f"   Role: {existing_admin.get('role', 'NOT SET')}")
            
            # Update password and role if needed
            hashed_password = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            await db.users.update_one(
                {"email": "admin@maidsofcyfair.com"},
                {"$set": {
                    "role": "admin",
                    "password_hash": hashed_password
                }}
            )
            print("✅ Updated admin password to: admin123")
        else:
            # Create new admin user
            hashed_password = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            admin_user = {
                "id": str(uuid.uuid4()),
                "email": "admin@maidsofcyfair.com",
                "password_hash": hashed_password,
                "first_name": "Admin",
                "last_name": "User",
                "role": "admin",
                "phone": "+1234567890",
                "created_at": datetime.utcnow(),
                "is_active": True
            }
            
            await db.users.insert_one(admin_user)
            print("✅ Created admin user:")
            print(f"   Email: admin@maidsofcyfair.com")
            print(f"   Password: admin123")
            print(f"   Role: admin")
            
        # Show all users
        print("\n📋 All users in database:")
        async for user in db.users.find({}, {"email": 1, "role": 1, "first_name": 1, "last_name": 1}):
            print(f"  - {user.get('email')}: {user.get('role')} ({user.get('first_name')} {user.get('last_name')})")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(create_admin_user())

