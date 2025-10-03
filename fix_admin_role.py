#!/usr/bin/env python3
"""
Script to fix admin user role in the database
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

# Database connection
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "maids_booking")

async def fix_admin_role():
    """Fix admin user role in the database"""
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    try:
        # Find admin user
        admin_user = await db.users.find_one({"email": "admin@maids.com"})
        
        if admin_user:
            print(f"Found admin user: {admin_user['email']}")
            print(f"Current role: {admin_user.get('role', 'NOT SET')}")
            
            # Update the role to 'admin'
            result = await db.users.update_one(
                {"email": "admin@maids.com"},
                {"$set": {"role": "admin"}}
            )
            
            if result.modified_count > 0:
                print("✅ Successfully updated admin role to 'admin'")
            else:
                print("⚠️  No changes made (role was already correct)")
        else:
            print("❌ Admin user not found")
            
        # Check all users and their roles
        print("\nAll users in database:")
        async for user in db.users.find({}, {"email": 1, "role": 1, "first_name": 1, "last_name": 1}):
            print(f"  - {user.get('email', 'NO EMAIL')}: {user.get('role', 'NO ROLE')} ({user.get('first_name', '')} {user.get('last_name', '')})")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(fix_admin_role())
