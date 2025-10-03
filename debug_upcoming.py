#!/usr/bin/env python3
"""
Debug the upcoming appointments endpoint
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta

async def debug_upcoming_appointments():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["test_database"]
    
    print("🔍 Debugging upcoming appointments query...")
    
    # Get current date and next month's date (same logic as endpoint)
    current_date = datetime.now().strftime("%Y-%m-%d")
    next_month = datetime.now() + timedelta(days=30)
    next_month_date = next_month.strftime("%Y-%m-%d")
    
    print(f"Current date: {current_date}")
    print(f"Next month date: {next_month_date}")
    
    # Test user ID
    test_user_id = "f208675f-5bdd-42f3-8198-632d523def4f"
    
    # Find upcoming bookings for this customer (same query as endpoint)
    query = {
        "customer_id": test_user_id,
        "booking_date": {"$gte": current_date, "$lte": next_month_date},
        "status": {"$in": ["pending", "confirmed"]}
    }
    
    print(f"Query: {query}")
    
    upcoming_bookings = await db.bookings.find(query).to_list(1000)
    
    print(f"Found {len(upcoming_bookings)} upcoming bookings")
    
    for booking in upcoming_bookings:
        print(f"  - ID: {booking.get('id', 'N/A')}")
        print(f"    Date: {booking.get('booking_date', 'N/A')}")
        print(f"    Status: {booking.get('status', 'N/A')}")
        print(f"    Amount: ${booking.get('total_amount', 0)}")
        print()
    
    # Also check all bookings for this user
    all_bookings = await db.bookings.find({"customer_id": test_user_id}).to_list(1000)
    print(f"Total bookings for user: {len(all_bookings)}")
    
    for booking in all_bookings:
        print(f"  - Date: {booking.get('booking_date', 'N/A')} (Status: {booking.get('status', 'N/A')})")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(debug_upcoming_appointments())
