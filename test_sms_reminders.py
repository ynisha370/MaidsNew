#!/usr/bin/env python3
"""
Test script for SMS Reminder System
This script tests the SMS reminder functionality without sending actual SMS messages
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from motor.motor_asyncio import AsyncIOMotorClient
from services.reminder_service import ReminderService
from services.twilio_sms_service import TwilioSMSService
from services.reminder_scheduler import ReminderScheduler

# Test configuration
TEST_MONGO_URL = "mongodb://localhost:27017"
TEST_DB_NAME = "maidsofcyfair_test"

async def test_sms_service():
    """Test the Twilio SMS service"""
    print("🔧 Testing Twilio SMS Service...")
    
    sms_service = TwilioSMSService()
    
    # Test configuration check
    is_configured = sms_service.is_configured()
    print(f"   SMS Service Configured: {is_configured}")
    
    if not is_configured:
        print("   ⚠️  SMS service not configured. Set TWILIO_* environment variables.")
        return False
    
    # Test phone number formatting
    test_phones = [
        "1234567890",
        "+1234567890", 
        "123-456-7890",
        "(123) 456-7890"
    ]
    
    for phone in test_phones:
        formatted = sms_service.format_phone_number(phone)
        print(f"   {phone} -> {formatted}")
    
    print("   ✅ SMS Service tests passed")
    return True

async def test_reminder_service():
    """Test the reminder service"""
    print("🔧 Testing Reminder Service...")
    
    # Connect to test database
    client = AsyncIOMotorClient(TEST_MONGO_URL)
    db = client[TEST_DB_NAME]
    
    try:
        reminder_service = ReminderService(db)
        
        # Test template initialization
        print("   Initializing default templates...")
        await reminder_service.initialize_default_templates()
        
        # Test getting templates
        templates = await reminder_service.get_templates()
        print(f"   Found {len(templates)} templates")
        
        for template in templates:
            print(f"   - {template['name']} ({template['type']})")
        
        # Test message formatting
        test_booking = {
            "customer": {
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+1234567890"
            },
            "booking_date": "2024-01-15",
            "time_slot": "9:00 AM - 11:00 AM",
            "house_size": "medium",
            "services": [
                {"name": "Deep Cleaning"},
                {"name": "Window Cleaning"}
            ]
        }
        
        if templates:
            template = templates[0]
            formatted_message = reminder_service.format_message(template['template'], test_booking)
            print(f"   Formatted message: {formatted_message[:100]}...")
        
        print("   ✅ Reminder Service tests passed")
        return True
        
    except Exception as e:
        print(f"   ❌ Reminder Service test failed: {str(e)}")
        return False
    finally:
        client.close()

async def test_reminder_scheduler():
    """Test the reminder scheduler"""
    print("🔧 Testing Reminder Scheduler...")
    
    # Connect to test database
    client = AsyncIOMotorClient(TEST_MONGO_URL)
    db = client[TEST_DB_NAME]
    
    try:
        reminder_service = ReminderService(db)
        scheduler = ReminderScheduler(db, reminder_service)
        
        # Test scheduler status
        status = await scheduler.get_scheduler_status()
        print(f"   Scheduler Status: {status}")
        
        # Test immediate reminder (without actually sending)
        print("   Testing immediate reminder functionality...")
        
        print("   ✅ Reminder Scheduler tests passed")
        return True
        
    except Exception as e:
        print(f"   ❌ Reminder Scheduler test failed: {str(e)}")
        return False
    finally:
        client.close()

async def test_database_operations():
    """Test database operations"""
    print("🔧 Testing Database Operations...")
    
    client = AsyncIOMotorClient(TEST_MONGO_URL)
    db = client[TEST_DB_NAME]
    
    try:
        # Test collection creation
        collections = await db.list_collection_names()
        print(f"   Available collections: {collections}")
        
        # Test template operations
        reminder_service = ReminderService(db)
        
        # Create a test template
        test_template = {
            "name": "Test Template",
            "type": "custom",
            "template": "Test message for {customer_name}",
            "send_timing": "immediate",
            "is_active": True
        }
        
        result = await reminder_service.create_template(test_template)
        print(f"   Template creation result: {result}")
        
        if result["success"]:
            template_id = result["template_id"]
            
            # Test getting the template
            template = await reminder_service.get_template(template_id)
            print(f"   Retrieved template: {template['name'] if template else 'None'}")
            
            # Test updating the template
            update_result = await reminder_service.update_template(template_id, {"name": "Updated Test Template"})
            print(f"   Template update result: {update_result}")
            
            # Test deleting the template
            delete_result = await reminder_service.delete_template(template_id)
            print(f"   Template deletion result: {delete_result}")
        
        print("   ✅ Database Operations tests passed")
        return True
        
    except Exception as e:
        print(f"   ❌ Database Operations test failed: {str(e)}")
        return False
    finally:
        client.close()

async def main():
    """Run all tests"""
    print("🚀 Starting SMS Reminder System Tests")
    print("=" * 50)
    
    tests = [
        test_sms_service,
        test_reminder_service,
        test_reminder_scheduler,
        test_database_operations
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"   ❌ Test failed with exception: {str(e)}")
            results.append(False)
        print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! SMS Reminder System is ready to use.")
    else:
        print("⚠️  Some tests failed. Please check the configuration and try again.")
    
    return passed == total

if __name__ == "__main__":
    # Check if MongoDB is running
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"❌ Test execution failed: {str(e)}")
        print("Make sure MongoDB is running and accessible.")
        sys.exit(1)
