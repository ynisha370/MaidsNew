#!/usr/bin/env python3
"""
Test user ID matching
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def test_user_id():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["test_database"]
    
    print("🔍 Testing user ID matching...")
    
    # Test user ID from JWT token
    test_user_id = "f208675f-5bdd-42f3-8198-632d523def4f"
    
    # Check if user exists
    user = await db.users.find_one({"id": test_user_id})
    if user:
        print(f"✅ User found: {user['email']} (ID: {user['id']})")
    else:
        print(f"❌ User not found with ID: {test_user_id}")
        
        # Check all users
        all_users = await db.users.find().to_list(1000)
        print(f"Total users in database: {len(all_users)}")
        for u in all_users:
            print(f"  - ID: {u.get('id', 'N/A')}, Email: {u.get('email', 'N/A')}")
    
    # Check bookings for this user
    bookings = await db.bookings.find({"customer_id": test_user_id}).to_list(1000)
    print(f"Bookings for user {test_user_id}: {len(bookings)}")
    
    for booking in bookings:
        print(f"  - Booking ID: {booking.get('id', 'N/A')}")
        print(f"    Customer ID: {booking.get('customer_id', 'N/A')}")
        print(f"    Date: {booking.get('booking_date', 'N/A')}")
        print(f"    Status: {booking.get('status', 'N/A')}")
        print()
    
    client.close()

if __name__ == "__main__":
    asyncio.run(test_user_id())
