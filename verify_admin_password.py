#!/usr/bin/env python3
import asyncio
import os
import bcrypt
from motor.motor_asyncio import AsyncIOMotorClient

# Database connection
MONGODB_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DB_NAME", "maidsofcyfair")

# Fix MongoDB URL if it has special characters
if "qHdDNJMRw8@123" in MONGODB_URL:
    MONGODB_URL = MONGODB_URL.replace("qHdDNJMRw8@123", "qHdDNJMRw8%40123")

async def verify_password():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    try:
        admin = await db.users.find_one({"email": "admin@maidsofcyfair.com"})
        
        if admin:
            print("Admin user found:")
            print(f"  Email: {admin['email']}")
            print(f"  ID: {admin['id']}")
            print(f"  Role: {admin.get('role')}")
            print(f"  Password hash: {admin['password_hash'][:50]}...")
            
            # Test password verification
            password = "admin123"
            hash_bytes = admin['password_hash'].encode('utf-8')
            password_bytes = password.encode('utf-8')
            
            print(f"\nTesting password verification:")
            print(f"  Password: {password}")
            result = bcrypt.checkpw(password_bytes, hash_bytes)
            print(f"  Result: {result}")
            
            if result:
                print("✅ Password verification successful!")
            else:
                print("❌ Password verification failed!")
                print("\nLet me create a new hash...")
                new_hash = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode('utf-8')
                print(f"  New hash: {new_hash[:50]}...")
                
                # Update the database
                await db.users.update_one(
                    {"email": "admin@maidsofcyfair.com"},
                    {"$set": {"password_hash": new_hash}}
                )
                print("✅ Updated password hash in database")
        else:
            print("❌ Admin user not found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(verify_password())

