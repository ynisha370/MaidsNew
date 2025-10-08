#!/usr/bin/env python3
"""
Demo Cleaner Account Setup Instructions
=====================================

This script provides instructions for setting up a demo cleaner account
for testing the cleaner dashboard functionality.

Since MongoDB may not be running locally, this script provides the data
structure needed to manually create the demo cleaner account.
"""

import json
import os
import bcrypt
from pathlib import Path

def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def main():
    """Display demo cleaner setup instructions"""

    print("CLEANER Demo Cleaner Account Setup Instructions")
    print("=" * 60)
    print()

    print("PROBLEM: 'Invalid email or password' error")
    print("SOLUTION: Demo cleaner account needs to be created in database")
    print()

    print("STEP 1: Set up MongoDB")
    print("Option A - Use local MongoDB:")
    print("   1. Install MongoDB Community Edition")
    print("   2. Start MongoDB: mongod")
    print("   3. Run: python setup_cloud_mongodb.py")
    print()
    print("Option B - Use MongoDB Atlas (cloud):")
    print("   1. Create free cluster at https://www.mongodb.com/atlas")
    print("   2. Get connection string")
    print("   3. Update backend/.env with MONGO_URL")
    print()

    print("STEP 2: Create demo cleaner account manually")
    print("Use MongoDB Compass or mongo shell to insert this data:")
    print()

    # Create the demo cleaner data
    demo_cleaner = {
        "id": "demo_cleaner_001",
        "email": "cleaner@maids.com",
        "password_hash": hash_password("cleaner@123"),
        "first_name": "Demo",
        "last_name": "Cleaner",
        "phone": "555-0123",
        "role": "cleaner",
        "address": {
            "street": "123 Demo Street",
            "city": "Houston",
            "state": "TX",
            "zip_code": "77001"
        },
        "experience_years": 3,
        "hourly_rate": 25.0,
        "specializations": ["Deep cleaning", "Move-in/out", "Post-construction"],
        "languages": ["English", "Spanish"],
        "certifications": ["OSHA Certified"],
        "emergency_contact_name": "Jane Doe",
        "emergency_contact_phone": "555-0987",
        "emergency_contact_relationship": "Spouse",
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }

    print("=== DEMO CLEANER DATA (Insert into 'users' collection) ===")
    print(json.dumps(demo_cleaner, indent=2))
    print()

    print("=== DEMO BOOKINGS DATA (Insert into 'bookings' collection) ===")

    demo_bookings = [
        {
            "id": "demo_booking_001",
            "user_id": "demo_customer_001",
            "cleaner_id": "demo_cleaner_001",
            "date": "2024-12-20",
            "start_time": "09:00",
            "end_time": "11:00",
            "status": "confirmed",
            "total_amount": 150.0,
            "duration_hours": 2,
            "address": "456 Customer Ave, Houston, TX 77002",
            "special_instructions": "Please bring extra cleaning supplies for deep cleaning.",
            "services": [
                {"name": "Deep Cleaning", "price": 100.0},
                {"name": "Bathroom Sanitization", "price": 50.0}
            ],
            "created_at": "2024-12-01T10:00:00Z",
            "updated_at": "2024-12-01T10:00:00Z"
        },
        {
            "id": "demo_booking_002",
            "user_id": "demo_customer_002",
            "cleaner_id": "demo_cleaner_001",
            "date": "2024-12-21",
            "start_time": "14:00",
            "end_time": "16:00",
            "status": "in_progress",
            "total_amount": 100.0,
            "duration_hours": 2,
            "address": "789 Oak Street, Houston, TX 77003",
            "special_instructions": "Regular maintenance cleaning.",
            "services": [
                {"name": "Standard Cleaning", "price": 80.0},
                {"name": "Kitchen Deep Clean", "price": 20.0}
            ],
            "created_at": "2024-12-02T14:00:00Z",
            "updated_at": "2024-12-02T14:00:00Z",
            "clock_in_time": "2024-12-21T14:00:00Z"
        },
        {
            "id": "demo_booking_003",
            "user_id": "demo_customer_003",
            "cleaner_id": "demo_cleaner_001",
            "date": "2024-12-19",
            "start_time": "10:00",
            "end_time": "12:00",
            "status": "completed",
            "total_amount": 120.0,
            "duration_hours": 2,
            "address": "321 Pine Road, Houston, TX 77004",
            "special_instructions": "Move-out cleaning required.",
            "services": [
                {"name": "Move-out Cleaning", "price": 120.0}
            ],
            "created_at": "2024-12-01T09:00:00Z",
            "updated_at": "2024-12-19T12:00:00Z",
            "clock_in_time": "2024-12-19T10:00:00Z",
            "clock_out_time": "2024-12-19T12:00:00Z"
        }
    ]

    for i, booking in enumerate(demo_bookings, 1):
        print(f"\n--- Demo Booking {i} ---")
        print(json.dumps(booking, indent=2))

    print("\n" + "=" * 60)
    print("STEP 3: Test the login")
    print("URL: http://localhost:3000/cleaner/login")
    print("Email: cleaner@maids.com")
    print("Password: cleaner@123")
    print()
    print("STEP 4: Access dashboard")
    print("URL: http://localhost:3000/cleaner")
    print()
    print("STEP 5: Verify features work")
    print("- View jobs in different statuses")
    print("- Clock in/out for jobs")
    print("- Update ETA for jobs")
    print("- View job details and customer information")
    print("- Filter and search jobs")
    print()
    print("SUCCESS: Cleaner dashboard should now be fully functional!")

if __name__ == "__main__":
    main()
