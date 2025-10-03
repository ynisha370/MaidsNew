#!/usr/bin/env python3
"""
Create test user and bookings for testing upcoming appointments
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import uuid
import bcrypt

async def create_test_user_and_bookings():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["test_database"]
    
    print("🔧 Creating test user and bookings...")
    
    # Create test user
    test_user_id = "f208675f-5bdd-42f3-8198-632d523def4f"  # Use the same ID from the JWT token
    
    # Check if user already exists
    existing_user = await db.users.find_one({"id": test_user_id})
    if existing_user:
        print(f"✅ Test user already exists: {existing_user['email']}")
    else:
        # Create test user
        user_data = {
            "id": test_user_id,
            "email": "test@maids.com",
            "first_name": "Test",
            "last_name": "Customer",
            "phone": "(555) 123-4567",
            "password_hash": bcrypt.hashpw("test@maids@1234".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            "role": "customer",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        await db.users.insert_one(user_data)
        print(f"✅ Created test user: {user_data['email']}")
    
    # Create test bookings for the test user
    test_bookings = [
        {
            "id": str(uuid.uuid4()),
            "user_id": test_user_id,
            "customer_id": test_user_id,
            "house_size": "1500-2000",
            "frequency": "weekly",
            "rooms": {
                "masterBedroom": True,
                "masterBathroom": True,
                "otherBedrooms": 2,
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
            "booking_date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
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
            "special_instructions": "Test booking 1 - tomorrow",
            "cleaner_id": None,
            "calendar_event_id": None,
            "estimated_duration_hours": 3,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": test_user_id,
            "customer_id": test_user_id,
            "house_size": "2000-2500",
            "frequency": "biweekly",
            "rooms": {
                "masterBedroom": True,
                "masterBathroom": True,
                "otherBedrooms": 3,
                "otherFullBathrooms": 2,
                "halfBathrooms": 1,
                "diningRoom": True,
                "kitchen": True,
                "livingRoom": True,
                "mediaRoom": True,
                "gameRoom": False,
                "office": True
            },
            "services": [{"service_id": "standard_cleaning", "quantity": 1}],
            "a_la_carte_services": [
                {"service_id": "oven_cleaning", "quantity": 1},
                {"service_id": "window_cleaning", "quantity": 4}
            ],
            "booking_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            "time_slot": "10:00-12:00",
            "base_price": 150.0,
            "room_price": 95.0,
            "a_la_carte_total": 75.0,
            "total_amount": 320.0,
            "status": "pending",
            "payment_status": "pending",
            "address": {
                "street": "456 Test Ave",
                "city": "Houston",
                "state": "TX",
                "zip_code": "77433"
            },
            "special_instructions": "Test booking 2 - next week",
            "cleaner_id": None,
            "calendar_event_id": None,
            "estimated_duration_hours": 4,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": test_user_id,
            "customer_id": test_user_id,
            "house_size": "1000-1500",
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
            "a_la_carte_services": [
                {"service_id": "oven_cleaning", "quantity": 1}
            ],
            "booking_date": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
            "time_slot": "16:00-18:00",
            "base_price": 100.0,
            "room_price": 60.0,
            "a_la_carte_total": 40.0,
            "total_amount": 200.0,
            "status": "confirmed",
            "payment_status": "completed",
            "address": {
                "street": "789 Test Blvd",
                "city": "Houston",
                "state": "TX",
                "zip_code": "77433"
            },
            "special_instructions": "Test booking 3 - in 2 weeks",
            "cleaner_id": None,
            "calendar_event_id": None,
            "estimated_duration_hours": 2,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    ]
    
    # Insert test bookings
    for booking in test_bookings:
        result = await db.bookings.insert_one(booking)
        print(f"✅ Created booking {booking['id']} for {booking['booking_date']} (${booking['total_amount']})")
    
    print(f"\n🎉 Created {len(test_bookings)} test bookings!")
    print("Now test the upcoming appointments endpoint to see if they appear.")
    
    # Verify the bookings were created
    user_bookings = await db.bookings.find({"customer_id": test_user_id}).to_list(1000)
    print(f"\n📊 Total bookings for test user: {len(user_bookings)}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_test_user_and_bookings())
