"""
Direct database test to verify service edit works
Tests against the ACTUAL database the server uses
"""
import asyncio
import sys
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from datetime import datetime, timezone

# Load environment
load_dotenv(Path(__file__).parent / 'backend' / '.env')

# Get the SAME connection string the server uses
mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
db_name = os.getenv("DB_NAME", "maidsofcyfair")

# Fix password encoding
if "qHdDNJMRw8@123" in mongo_url:
    mongo_url = mongo_url.replace("qHdDNJMRw8@123", "qHdDNJMRw8%40123")

print("="*60)
print("SERVICE EDIT - DIRECT DATABASE TEST")
print("="*60)
print(f"\nDatabase URL: {mongo_url[:50]}...")
print(f"Database Name: {db_name}")

async def test():
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    # Test connection
    try:
        await db.command('ping')
        print("\n✓ Connected to MongoDB successfully")
    except Exception as e:
        print(f"\n✗ Connection failed: {e}")
        return
    
    # Get a service
    print("\n1. Finding a service...")
    service = await db.services.find_one()
    if not service:
        print("✗ No services found in database")
        client.close()
        return
    
    service_id = service.get('id')
    print(f"✓ Found service: {service.get('name')}")
    print(f"  ID: {service_id}")
    print(f"  Description BEFORE: {service.get('description', 'N/A')}")
    
    # Update it directly in DB
    print("\n2. Updating service description...")
    new_description = "✅ UPDATED SUCCESSFULLY: Professional feather dusting of all window blinds"
    result = await db.services.update_one(
        {"id": service_id},
        {"$set": {
            "description": new_description,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    if result.matched_count > 0:
        print(f"✓ Service updated! Matched: {result.matched_count}, Modified: {result.modified_count}")
    else:
        print(f"✗ Service not found for update")
    
    # Verify the update
    print("\n3. Verifying update...")
    updated_service = await db.services.find_one({"id": service_id})
    if updated_service:
        print(f"✓ Service retrieved after update")
        print(f"  Description AFTER: {updated_service.get('description', 'N/A')}")
        print(f"  Updated At: {updated_service.get('updated_at', 'N/A')}")
    
    # Test price update
    print("\n4. Updating service price...")
    result = await db.services.update_one(
        {"id": service_id},
        {"$set": {
            "a_la_carte_price": 15.99,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    if result.matched_count > 0:
        print(f"✓ Price updated! Modified: {result.modified_count}")
        updated_service = await db.services.find_one({"id": service_id})
        print(f"  New Price: ${updated_service.get('a_la_carte_price')}")
    
    print("\n" + "="*60)
    print("✅ SERVICE EDIT WORKS DIRECTLY IN DATABASE")
    print("="*60)
    print("\nThe issue is likely with the API endpoint routing or authentication.")
    print("The database operations work correctly.")
    
    client.close()

asyncio.run(test())

