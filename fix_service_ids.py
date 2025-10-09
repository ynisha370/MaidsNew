"""
Fix services in cloud database by adding 'id' field
"""
import asyncio
import sys
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
import uuid

# Load environment
load_dotenv(Path(__file__).parent / 'backend' / '.env')

# Get the SAME connection string the server uses
mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
db_name = os.getenv("DB_NAME", "maidsofcyfair")

# Fix password encoding
if "qHdDNJMRw8@123" in mongo_url:
    mongo_url = mongo_url.replace("qHdDNJMRw8@123", "qHdDNJMRw8%40123")

print("="*60)
print("FIXING SERVICE IDs IN CLOUD DATABASE")
print("="*60)

async def fix_services():
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    # Test connection
    try:
        await db.command('ping')
        print("\n✓ Connected to MongoDB successfully")
    except Exception as e:
        print(f"\n✗ Connection failed: {e}")
        return
    
    # Get all services
    services = await db.services.find().to_list(1000)
    print(f"\n✓ Found {len(services)} services")
    
    # Fix each service that's missing 'id'
    fixed_count = 0
    skipped_count = 0
    
    for service in services:
        if not service.get('id'):
            # Generate a new ID
            new_id = str(uuid.uuid4())
            
            # Update the service
            await db.services.update_one(
                {"_id": service['_id']},
                {"$set": {"id": new_id}}
            )
            
            print(f"  ✓ Fixed: {service.get('name')} → ID: {new_id}")
            fixed_count += 1
        else:
            print(f"  ⏭️  Skipped: {service.get('name')} (already has ID: {service.get('id')})")
            skipped_count += 1
    
    print(f"\n" + "="*60)
    print(f"SUMMARY:")
    print(f"  Fixed: {fixed_count} services")
    print(f"  Skipped: {skipped_count} services (already had IDs)")
    print(f"  Total: {len(services)} services")
    print("="*60)
    
    # Verify
    print(f"\nVerifying...")
    services_without_id = await db.services.count_documents({"id": {"$exists": False}})
    services_with_id = await db.services.count_documents({"id": {"$exists": True}})
    
    print(f"  Services without 'id': {services_without_id}")
    print(f"  Services with 'id': {services_with_id}")
    
    if services_without_id == 0:
        print(f"\n✅ ALL SERVICES NOW HAVE 'id' FIELD!")
    else:
        print(f"\n⚠️  {services_without_id} services still missing 'id'")
    
    client.close()

asyncio.run(fix_services())

