#!/usr/bin/env python3
"""
Demo Data Setup Script
Creates demo cleaners, customers, and bookings for comprehensive testing
"""

import asyncio
import bcrypt
from motor.motor_asyncio import AsyncIOMotorClient
import uuid
from datetime import datetime, timezone, timedelta

# Configuration
MONGO_URL = "mongodb+srv://ynitin370:qHdDNJMRw8%40123@maidsofcyfair.rplwzsy.mongodb.net/?retryWrites=true&w=majority&appName=maidsofcyfair"
DB_NAME = "maidsofcyfair"

class DemoDataSetup:
    def __init__(self):
        self.client = AsyncIOMotorClient(MONGO_URL)
        self.db = self.client[DB_NAME]
        self.created_cleaners = []
        self.created_customers = []
        self.created_bookings = []

    def hash_password(self, password):
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    async def create_demo_cleaners(self):
        """Create demo cleaners with user accounts"""
        print("🧹 Creating demo cleaners...")
        
        demo_cleaners = [
            {
                "id": "demo_cleaner_001",
                "email": "sarah.johnson@maids.com",
                "first_name": "Sarah",
                "last_name": "Johnson",
                "phone": "(281) 555-0101",
                "is_active": True,
                "is_approved": True,
                "rating": 4.8,
                "total_jobs": 45,
                "hourly_rate": 25.0,
                "specializations": ["Deep cleaning", "Move-in/out", "Post-construction"],
                "languages": ["English", "Spanish"],
                "address": {
                    "street": "100 Cleaner St",
                    "city": "Houston",
                    "state": "TX",
                    "zip_code": "77001"
                },
                "experience_years": 5,
                "certifications": ["OSHA Certified", "Green Cleaning Certified"],
                "emergency_contact_name": "Mike Johnson",
                "emergency_contact_phone": "(281) 555-0102",
                "emergency_contact_relationship": "Spouse",
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": "demo_cleaner_002",
                "email": "maria.garcia@maids.com",
                "first_name": "Maria",
                "last_name": "Garcia",
                "phone": "(281) 555-0201",
                "is_active": True,
                "is_approved": True,
                "rating": 4.6,
                "total_jobs": 32,
                "hourly_rate": 23.0,
                "specializations": ["Regular cleaning", "Kitchen deep clean", "Bathroom sanitization"],
                "languages": ["English", "Spanish", "Portuguese"],
                "address": {
                    "street": "200 Service Ave",
                    "city": "Houston",
                    "state": "TX",
                    "zip_code": "77002"
                },
                "experience_years": 3,
                "certifications": ["Green Cleaning Certified"],
                "emergency_contact_name": "Carlos Garcia",
                "emergency_contact_phone": "(281) 555-0202",
                "emergency_contact_relationship": "Brother",
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": "demo_cleaner_003",
                "email": "jennifer.smith@maids.com",
                "first_name": "Jennifer",
                "last_name": "Smith",
                "phone": "(281) 555-0301",
                "is_active": True,
                "is_approved": True,
                "rating": 4.9,
                "total_jobs": 67,
                "hourly_rate": 27.0,
                "specializations": ["Post-construction", "Deep cleaning", "Window cleaning"],
                "languages": ["English"],
                "address": {
                    "street": "300 Professional Blvd",
                    "city": "Houston",
                    "state": "TX",
                    "zip_code": "77003"
                },
                "experience_years": 7,
                "certifications": ["OSHA Certified", "Green Cleaning Certified", "Window Cleaning Specialist"],
                "emergency_contact_name": "David Smith",
                "emergency_contact_phone": "(281) 555-0302",
                "emergency_contact_relationship": "Husband",
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": "demo_cleaner_004",
                "email": "lisa.wilson@maids.com",
                "first_name": "Lisa",
                "last_name": "Wilson",
                "phone": "(281) 555-0401",
                "is_active": True,
                "is_approved": True,
                "rating": 4.7,
                "total_jobs": 28,
                "hourly_rate": 24.0,
                "specializations": ["Regular cleaning", "Office cleaning", "Move-in/out"],
                "languages": ["English", "French"],
                "address": {
                    "street": "400 Quality Dr",
                    "city": "Houston",
                    "state": "TX",
                    "zip_code": "77004"
                },
                "experience_years": 4,
                "certifications": ["Green Cleaning Certified"],
                "emergency_contact_name": "Robert Wilson",
                "emergency_contact_phone": "(281) 555-0402",
                "emergency_contact_relationship": "Father",
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": "demo_cleaner_005",
                "email": "ana.rodriguez@maids.com",
                "first_name": "Ana",
                "last_name": "Rodriguez",
                "phone": "(281) 555-0501",
                "is_active": True,
                "is_approved": True,
                "rating": 4.5,
                "total_jobs": 19,
                "hourly_rate": 22.0,
                "specializations": ["Regular cleaning", "Deep cleaning"],
                "languages": ["English", "Spanish"],
                "address": {
                    "street": "500 Excellence Ln",
                    "city": "Houston",
                    "state": "TX",
                    "zip_code": "77005"
                },
                "experience_years": 2,
                "certifications": ["Green Cleaning Certified"],
                "emergency_contact_name": "Miguel Rodriguez",
                "emergency_contact_phone": "(281) 555-0502",
                "emergency_contact_relationship": "Husband",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        ]

        for cleaner_data in demo_cleaners:
            # Check if cleaner already exists
            existing_cleaner = await self.db.cleaners.find_one({"email": cleaner_data["email"]})
            if existing_cleaner:
                print(f"ℹ️  Cleaner already exists: {cleaner_data['first_name']} {cleaner_data['last_name']}")
                self.created_cleaners.append(existing_cleaner)
                continue

            # Insert cleaner profile
            await self.db.cleaners.insert_one(cleaner_data)
            print(f"✅ Created cleaner: {cleaner_data['first_name']} {cleaner_data['last_name']}")
            self.created_cleaners.append(cleaner_data)

            # Create user account for cleaner
            user_data = {
                "id": cleaner_data["id"],
                "email": cleaner_data["email"],
                "password_hash": self.hash_password("cleaner123"),
                "first_name": cleaner_data["first_name"],
                "last_name": cleaner_data["last_name"],
                "phone": cleaner_data["phone"],
                "role": "cleaner",
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            }

            existing_user = await self.db.users.find_one({"email": user_data["email"]})
            if not existing_user:
                await self.db.users.insert_one(user_data)
                print(f"✅ Created user account for: {user_data['first_name']} {user_data['last_name']}")

        print(f"🎉 Created {len(self.created_cleaners)} demo cleaners")

    async def create_demo_customers(self):
        """Create demo customers"""
        print("\n👥 Creating demo customers...")
        
        demo_customers = [
            {
                "id": "demo_customer_001",
                "email": "john.doe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "(281) 555-1001",
                "role": "customer",
                "is_active": True,
                "address": {
                    "street": "123 Main Street",
                    "city": "Houston",
                    "state": "TX",
                    "zip_code": "77001"
                },
                "preferences": {
                    "frequency": "weekly",
                    "special_instructions": "Focus on kitchen and bathrooms",
                    "preferred_time": "morning"
                },
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": "demo_customer_002",
                "email": "jane.smith@example.com",
                "first_name": "Jane",
                "last_name": "Smith",
                "phone": "(281) 555-1002",
                "role": "customer",
                "is_active": True,
                "address": {
                    "street": "456 Oak Avenue",
                    "city": "Houston",
                    "state": "TX",
                    "zip_code": "77002"
                },
                "preferences": {
                    "frequency": "biweekly",
                    "special_instructions": "Pet-friendly cleaning products only",
                    "preferred_time": "afternoon"
                },
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": "demo_customer_003",
                "email": "mike.wilson@example.com",
                "first_name": "Mike",
                "last_name": "Wilson",
                "phone": "(281) 555-1003",
                "role": "customer",
                "is_active": True,
                "address": {
                    "street": "789 Pine Road",
                    "city": "Houston",
                    "state": "TX",
                    "zip_code": "77003"
                },
                "preferences": {
                    "frequency": "one_time",
                    "special_instructions": "Move-out cleaning required",
                    "preferred_time": "morning"
                },
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": "demo_customer_004",
                "email": "sarah.brown@example.com",
                "first_name": "Sarah",
                "last_name": "Brown",
                "phone": "(281) 555-1004",
                "role": "customer",
                "is_active": True,
                "address": {
                    "street": "321 Elm Street",
                    "city": "Houston",
                    "state": "TX",
                    "zip_code": "77004"
                },
                "preferences": {
                    "frequency": "monthly",
                    "special_instructions": "Deep clean every visit",
                    "preferred_time": "afternoon"
                },
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        ]

        for customer_data in demo_customers:
            existing_customer = await self.db.users.find_one({"email": customer_data["email"]})
            if existing_customer:
                print(f"ℹ️  Customer already exists: {customer_data['first_name']} {customer_data['last_name']}")
                self.created_customers.append(existing_customer)
                continue

            customer_data["password_hash"] = self.hash_password("customer123")
            await self.db.users.insert_one(customer_data)
            print(f"✅ Created customer: {customer_data['first_name']} {customer_data['last_name']}")
            self.created_customers.append(customer_data)

        print(f"🎉 Created {len(self.created_customers)} demo customers")

    async def create_demo_bookings(self):
        """Create demo bookings and assign them to cleaners"""
        print("\n📅 Creating demo bookings...")
        
        # Create bookings for different dates
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        day_after = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
        next_week = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        next_week_plus_1 = (datetime.now() + timedelta(days=8)).strftime("%Y-%m-%d")
        next_week_plus_2 = (datetime.now() + timedelta(days=9)).strftime("%Y-%m-%d")

        demo_bookings = [
            {
                "id": "demo_booking_001",
                "customer_id": self.created_customers[0]["id"],
                "cleaner_id": self.created_cleaners[0]["id"],
                "house_size": "3_bedroom",
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
                "booking_date": tomorrow,
                "time_slot": "09:00-12:00",
                "base_price": 120.0,
                "room_price": 74.8,
                "a_la_carte_total": 0.0,
                "total_amount": 194.8,
                "status": "confirmed",
                "payment_status": "paid",
                "address": {
                    "street": "123 Main Street",
                    "city": "Houston",
                    "state": "TX",
                    "zip_code": "77001"
                },
                "special_instructions": "Please focus on kitchen and bathrooms. Use pet-friendly products.",
                "estimated_duration_hours": 3,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": "demo_booking_002",
                "customer_id": self.created_customers[1]["id"],
                "cleaner_id": self.created_cleaners[1]["id"],
                "house_size": "4_bedroom",
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
                "booking_date": day_after,
                "time_slot": "14:00-17:00",
                "base_price": 150.0,
                "room_price": 95.0,
                "a_la_carte_total": 75.0,
                "total_amount": 320.0,
                "status": "confirmed",
                "payment_status": "paid",
                "address": {
                    "street": "456 Oak Avenue",
                    "city": "Houston",
                    "state": "TX",
                    "zip_code": "77002"
                },
                "special_instructions": "Deep clean required for move-in. Focus on all bathrooms and kitchen.",
                "estimated_duration_hours": 4,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": "demo_booking_003",
                "customer_id": self.created_customers[2]["id"],
                "cleaner_id": self.created_cleaners[2]["id"],
                "house_size": "2_bedroom",
                "frequency": "one_time",
                "rooms": {
                    "masterBedroom": True,
                    "masterBathroom": True,
                    "otherBedrooms": 1,
                    "otherFullBathrooms": 1,
                    "halfBathrooms": 0,
                    "diningRoom": False,
                    "kitchen": True,
                    "livingRoom": True,
                    "mediaRoom": False,
                    "gameRoom": False,
                    "office": False
                },
                "services": [{"service_id": "standard_cleaning", "quantity": 1}],
                "a_la_carte_services": [],
                "booking_date": next_week,
                "time_slot": "10:00-13:00",
                "base_price": 100.0,
                "room_price": 60.0,
                "a_la_carte_total": 0.0,
                "total_amount": 160.0,
                "status": "pending",
                "payment_status": "pending",
                "address": {
                    "street": "789 Pine Road",
                    "city": "Houston",
                    "state": "TX",
                    "zip_code": "77003"
                },
                "special_instructions": "Move-out cleaning required. Empty all cabinets and clean thoroughly.",
                "estimated_duration_hours": 3,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": "demo_booking_004",
                "customer_id": self.created_customers[3]["id"],
                "cleaner_id": self.created_cleaners[3]["id"],
                "house_size": "5_bedroom",
                "frequency": "monthly",
                "rooms": {
                    "masterBedroom": True,
                    "masterBathroom": True,
                    "otherBedrooms": 4,
                    "otherFullBathrooms": 3,
                    "halfBathrooms": 1,
                    "diningRoom": True,
                    "kitchen": True,
                    "livingRoom": True,
                    "mediaRoom": True,
                    "gameRoom": True,
                    "office": True
                },
                "services": [{"service_id": "standard_cleaning", "quantity": 1}],
                "a_la_carte_services": [
                    {"service_id": "oven_cleaning", "quantity": 1},
                    {"service_id": "window_cleaning", "quantity": 8},
                    {"service_id": "refrigerator_cleaning", "quantity": 1}
                ],
                "booking_date": next_week_plus_1,
                "time_slot": "08:00-12:00",
                "base_price": 200.0,
                "room_price": 120.0,
                "a_la_carte_total": 150.0,
                "total_amount": 470.0,
                "status": "confirmed",
                "payment_status": "paid",
                "address": {
                    "street": "321 Elm Street",
                    "city": "Houston",
                    "state": "TX",
                    "zip_code": "77004"
                },
                "special_instructions": "Monthly deep clean. Include all a-la-carte services. Focus on high-traffic areas.",
                "estimated_duration_hours": 4,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": "demo_booking_005",
                "customer_id": self.created_customers[0]["id"],
                "cleaner_id": self.created_cleaners[4]["id"],
                "house_size": "2_bedroom",
                "frequency": "weekly",
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
                    {"service_id": "window_cleaning", "quantity": 2}
                ],
                "booking_date": next_week_plus_2,
                "time_slot": "13:00-16:00",
                "base_price": 110.0,
                "room_price": 70.0,
                "a_la_carte_total": 30.0,
                "total_amount": 210.0,
                "status": "in_progress",
                "payment_status": "paid",
                "address": {
                    "street": "123 Main Street",
                    "city": "Houston",
                    "state": "TX",
                    "zip_code": "77001"
                },
                "special_instructions": "Regular weekly cleaning with window cleaning for living room and master bedroom.",
                "estimated_duration_hours": 3,
                "clock_in_time": datetime.now(timezone.utc).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        ]

        for booking_data in demo_bookings:
            existing_booking = await self.db.bookings.find_one({"id": booking_data["id"]})
            if existing_booking:
                print(f"ℹ️  Booking already exists: {booking_data['id']}")
                self.created_bookings.append(existing_booking)
                continue

            await self.db.bookings.insert_one(booking_data)
            print(f"✅ Created booking: {booking_data['id']} for {booking_data['booking_date']} - {booking_data['time_slot']}")
            self.created_bookings.append(booking_data)

        print(f"🎉 Created {len(self.created_bookings)} demo bookings")

    async def create_cleaner_availability(self):
        """Create cleaner availability records"""
        print("\n📅 Setting up cleaner availability...")
        
        # Create availability for next 7 days only (faster setup)
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=7)
        
        time_slots = ["08:00-10:00", "10:00-12:00", "12:00-14:00", "14:00-16:00", "16:00-18:00"]
        
        for cleaner in self.created_cleaners:
            cleaner_id = cleaner["id"]
            availability_count = 0
            
            current_date = start_date
            while current_date <= end_date:
                for time_slot in time_slots:
                    # Check if this slot is already booked
                    existing_booking = await self.db.bookings.find_one({
                        "cleaner_id": cleaner_id,
                        "booking_date": current_date.strftime("%Y-%m-%d"),
                        "time_slot": time_slot,
                        "status": {"$in": ["confirmed", "in_progress"]}
                    })
                    
                    is_booked = existing_booking is not None
                    
                    availability_record = {
                        "cleaner_id": cleaner_id,
                        "date": current_date.strftime("%Y-%m-%d"),
                        "time_slot": time_slot,
                        "is_available": True,
                        "is_booked": is_booked,
                        "booking_id": existing_booking["id"] if existing_booking else None,
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                    
                    # Check if availability record already exists
                    existing_availability = await self.db.cleaner_availability.find_one({
                        "cleaner_id": cleaner_id,
                        "date": current_date.strftime("%Y-%m-%d"),
                        "time_slot": time_slot
                    })
                    
                    if not existing_availability:
                        await self.db.cleaner_availability.insert_one(availability_record)
                        availability_count += 1
                
                current_date += timedelta(days=1)
            
            print(f"✅ Created {availability_count} availability records for {cleaner['first_name']} {cleaner['last_name']}")
        
        print(f"🎉 Cleaner availability setup completed for {len(self.created_cleaners)} cleaners")

    async def setup_all_demo_data(self):
        """Setup all demo data"""
        print("🚀 Setting up comprehensive demo data...")
        print("="*60)
        
        try:
            await self.create_demo_cleaners()
            await self.create_demo_customers()
            await self.create_demo_bookings()
            await self.create_cleaner_availability()
            
            print("\n" + "="*60)
            print("🎉 DEMO DATA SETUP COMPLETE!")
            print("="*60)
            print(f"✅ Created {len(self.created_cleaners)} cleaners")
            print(f"✅ Created {len(self.created_customers)} customers")
            print(f"✅ Created {len(self.created_bookings)} bookings")
            print("\n📋 Demo Cleaner Login Credentials:")
            for cleaner in self.created_cleaners:
                print(f"   Email: {cleaner['email']}")
                print(f"   Password: cleaner123")
                print(f"   Name: {cleaner['first_name']} {cleaner['last_name']}")
                print()
            
            print("📋 Demo Customer Login Credentials:")
            for customer in self.created_customers:
                print(f"   Email: {customer['email']}")
                print(f"   Password: customer123")
                print(f"   Name: {customer['first_name']} {customer['last_name']}")
                print()
                
        except Exception as e:
            print(f"❌ Error setting up demo data: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            self.client.close()

async def main():
    """Main function to setup demo data"""
    setup = DemoDataSetup()
    await setup.setup_all_demo_data()

if __name__ == "__main__":
    asyncio.run(main())
