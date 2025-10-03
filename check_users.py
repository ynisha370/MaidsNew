
#!/usr/bin/env python3
"""
Check users in the database
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check_users():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["test_database"]
    
    print("🔍 Checking users in database...")
    
    # Get all users
    users = await db.users.find().to_list(1000)
    print(f"Total users in database: {len(users)}")
    
    if users:
        print("\n👥 Users found:")
        for user in users:
            print(f"  - Email: {user.get('email', 'N/A')}")
            print(f"    Name: {user.get('first_name', 'N/A')} {user.get('last_name', 'N/A')}")
            print(f"    Role: {user.get('role', 'N/A')}")
            print(f"    ID: {user.get('id', 'N/A')}")
            print()
    else:
        print("❌ No users found in database")
    
    # Check if test user exists
    test_user = await db.users.find_one({"email": "test@maids.com"})
    if test_user:
        print(f"✅ Test user found: {test_user['id']}")
    else:
        print("❌ Test user not found")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_users())
