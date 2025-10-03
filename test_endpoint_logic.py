#!/usr/bin/env python3
"""
Test the exact logic from the upcoming appointments endpoint
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta

async def test_endpoint_logic():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["test_database"]
    
    print("🔍 Testing exact endpoint logic...")
    
    # Exact same logic as the endpoint
    current_date = datetime.now().strftime("%Y-%m-%d")
    next_month = datetime.now() + timedelta(days=30)
    next_month_date = next_month.strftime("%Y-%m-%d")
    
    print(f"Current date: {current_date}")
    print(f"Next month date: {next_month_date}")
    
    test_user_id = "f208675f-5bdd-42f3-8198-632d523def4f"
    
    # Exact same query as the endpoint
    query = {
        "customer_id": test_user_id,
        "booking_date": {"$gte": current_date, "$lte": next_month_date},
        "status": {"$in": ["pending", "confirmed"]}
    }
    
    print(f"Query: {query}")
    
    upcoming_bookings = await db.bookings.find(query).to_list(1000)
    print(f"Found {len(upcoming_bookings)} bookings")
    
    for booking in upcoming_bookings:
        print(f"  - ID: {booking.get('id', 'N/A')}")
        print(f"    Date: {booking.get('booking_date', 'N/A')}")
        print(f"    Status: {booking.get('status', 'N/A')}")
        print(f"    Amount: ${booking.get('total_amount', 0)}")
        print()
    
    # Test individual parts of the query
    print("\n🔍 Testing individual query parts...")
    
    # Test customer_id only
    customer_bookings = await db.bookings.find({"customer_id": test_user_id}).to_list(1000)
    print(f"Bookings for customer_id: {len(customer_bookings)}")
    
    # Test date range only
    date_bookings = await db.bookings.find({
        "booking_date": {"$gte": current_date, "$lte": next_month_date}
    }).to_list(1000)
    print(f"Bookings in date range: {len(date_bookings)}")
    
    # Test status only
    status_bookings = await db.bookings.find({
        "status": {"$in": ["pending", "confirmed"]}
    }).to_list(1000)
    print(f"Bookings with correct status: {len(status_bookings)}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(test_endpoint_logic())
