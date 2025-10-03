#!/usr/bin/env python3
"""
Create a booking for today to test the endpoint
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import uuid

async def create_today_booking():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["test_database"]
    
    print("🔧 Creating booking for today...")
    
    test_user_id = "f208675f-5bdd-42f3-8198-632d523def4f"
    
    # Create a booking for today
    today = datetime.now().strftime("%Y-%m-%d")
    
    booking = {
        "id": str(uuid.uuid4()),
        "user_id": test_user_id,
        "customer_id": test_user_id,
        "house_size": "1500-2000",
        "frequency": "one_time",
        "rooms": {
            "masterBedroom": True,
            "masterBathroom": True,
            "otherBedrooms": 1,
            "otherFullBathrooms": 1,
            "halfBathrooms": 0,
            "diningRoom": True,
            "kitchen": True,
            "livingRoom": True,
            "mediaRoom": False,
            "gameRoom": False,
            "office": False
        },
        "services": [{"service_id": "standard_cleaning", "quantity": 1}],
        "a_la_carte_services": [],
        "booking_date": today,
        "time_slot": "14:00-16:00",
        "base_price": 120.0,
        "room_price": 74.8,
        "a_la_carte_total": 0.0,
        "total_amount": 194.8,
        "status": "confirmed",
        "payment_status": "completed",
        "address": {
            "street": "123 Test St",
            "city": "Houston",
            "state": "TX",
            "zip_code": "77433"
        },
        "special_instructions": "Test booking for today",
        "cleaner_id": None,
        "calendar_event_id": None,
        "estimated_duration_hours": 3,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    result = await db.bookings.insert_one(booking)
    print(f"✅ Created booking for today ({today}): {booking['id']}")
    
    # Test the query
    current_date = datetime.now().strftime("%Y-%m-%d")
    next_month = datetime.now() + timedelta(days=30)
    next_month_date = next_month.strftime("%Y-%m-%d")
    
    query = {
        "customer_id": test_user_id,
        "booking_date": {"$gte": current_date, "$lte": next_month_date},
        "status": {"$in": ["pending", "confirmed"]}
    }
    
    upcoming_bookings = await db.bookings.find(query).to_list(1000)
    print(f"Query result: {len(upcoming_bookings)} bookings found")
    
    for booking in upcoming_bookings:
        print(f"  - Date: {booking.get('booking_date', 'N/A')}, Status: {booking.get('status', 'N/A')}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_today_booking())
