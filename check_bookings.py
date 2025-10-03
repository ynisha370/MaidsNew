#!/usr/bin/env python3
"""
Check existing bookings in the database
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta

async def check_bookings():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["test_database"]
    
    print("🔍 Checking existing bookings...")
    
    # Get all bookings
    bookings = await db.bookings.find().to_list(1000)
    print(f"Total bookings in database: {len(bookings)}")
    
    if bookings:
        print("\n📋 Recent bookings:")
        for booking in bookings[-5:]:  # Show last 5 bookings
            print(f"  - ID: {booking.get('id', 'N/A')}")
            print(f"    Customer ID: {booking.get('customer_id', 'N/A')}")
            print(f"    Date: {booking.get('booking_date', 'N/A')}")
            print(f"    Status: {booking.get('status', 'N/A')}")
            print(f"    Amount: ${booking.get('total_amount', 0)}")
            print()
    
    # Check for bookings for our test user
    test_user_id = "f208675f-5bdd-42f3-8198-632d523def4f"
    user_bookings = await db.bookings.find({"customer_id": test_user_id}).to_list(1000)
    print(f"Bookings for test user ({test_user_id}): {len(user_bookings)}")
    
    if user_bookings:
        print("\n👤 Test user bookings:")
        for booking in user_bookings:
            print(f"  - Date: {booking.get('booking_date', 'N/A')}")
            print(f"    Status: {booking.get('status', 'N/A')}")
            print(f"    Amount: ${booking.get('total_amount', 0)}")
            print()
    
    # Check upcoming bookings (next 30 days)
    current_date = datetime.now().strftime("%Y-%m-%d")
    next_month = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    
    upcoming_bookings = await db.bookings.find({
        "customer_id": test_user_id,
        "booking_date": {"$gte": current_date, "$lte": next_month},
        "status": {"$in": ["pending", "confirmed"]}
    }).to_list(1000)
    
    print(f"Upcoming bookings for test user: {len(upcoming_bookings)}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_bookings())
