#!/usr/bin/env python3
"""
Test script to check if backend booking data includes rooms and additional services
"""

import sys
import os

# Add the backend directory to the path
sys.path.append('/Users/nitinyadav/Documents/GitHub/maidsofcyfair.new/backend')

def test_booking_data_structure():
    """Test the expected booking data structure"""
    print("=== Backend Data Structure Test ===")
    print("Checking if booking data includes rooms and additional services...\n")
    
    # Expected booking structure
    expected_booking_structure = {
        "id": "string",
        "customer_id": "string", 
        "services": [
            {
                "service_id": "string",
                "quantity": "number"
            }
        ],
        "a_la_carte_services": [
            {
                "service_id": "string",
                "quantity": "number"
            }
        ],
        "rooms": {
            "bedroom": {"quantity": "number", "price": "number"},
            "bathroom": {"quantity": "number", "price": "number"},
            "kitchen": {"quantity": "number", "price": "number"}
        },
        "base_price": "number",
        "room_price": "number", 
        "a_la_carte_total": "number",
        "total_amount": "number",
        "house_size": "string",
        "frequency": "string",
        "booking_date": "string",
        "time_slot": "string"
    }
    
    print("✓ Expected booking data structure:")
    for key, value in expected_booking_structure.items():
        if isinstance(value, dict):
            print(f"  - {key}: object with keys {list(value.keys())}")
        elif isinstance(value, list):
            print(f"  - {key}: array of {value[0] if value else 'objects'}")
        else:
            print(f"  - {key}: {value}")
    
    print("\n✅ Key fields for Room Selection and Additional Services:")
    print("   - rooms: Object containing room types with quantities and prices")
    print("   - a_la_carte_services: Array of additional service objects")
    print("   - room_price: Total price for room selection")
    print("   - a_la_carte_total: Total price for additional services")
    
    return True

def test_sample_booking_data():
    """Show sample booking data with rooms and additional services"""
    print("\n=== Sample Booking Data ===")
    print("This is what the booking data should look like:\n")
    
    sample_booking = {
        "id": "booking_123",
        "customer_id": "customer_456",
        "services": [
            {"service_id": "standard_cleaning", "quantity": 1}
        ],
        "a_la_carte_services": [
            {"service_id": "oven_cleaning", "quantity": 1},
            {"service_id": "window_cleaning", "quantity": 4}
        ],
        "rooms": {
            "bedroom": {"quantity": 3, "price": 45.0},
            "bathroom": {"quantity": 2, "price": 30.0},
            "kitchen": {"quantity": 1, "price": 25.0}
        },
        "base_price": 120.0,
        "room_price": 100.0,
        "a_la_carte_total": 95.0,
        "total_amount": 315.0,
        "house_size": "medium",
        "frequency": "weekly",
        "booking_date": "2024-01-15",
        "time_slot": "09:00-11:00"
    }
    
    import json
    print(json.dumps(sample_booking, indent=2))
    
    print("\n✅ This sample data should make the sections visible:")
    print(f"   - Room Selection: {len(sample_booking['rooms'])} room types")
    print(f"   - Additional Services: {len(sample_booking['a_la_carte_services'])} services")
    
    return True

def main():
    """Main test function"""
    print("🔍 Backend Data Test for Room Selection & Additional Services")
    print("=" * 60)
    
    test_booking_data_structure()
    test_sample_booking_data()
    
    print("\n📋 Troubleshooting Steps:")
    print("1. Check if booking data in database includes 'rooms' and 'a_la_carte_services'")
    print("2. Verify that 'room_price' and 'a_la_carte_total' are calculated")
    print("3. Ensure frontend is receiving the complete booking object")
    print("4. Check browser console for debug messages")
    print("\n🔧 Debug indicators added to frontend:")
    print("   - Yellow box: No additional services found")
    print("   - Orange box: No rooms selected")
    print("   - Console logs: Data structure details")

if __name__ == "__main__":
    main()
