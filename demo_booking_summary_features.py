#!/usr/bin/env python3
"""
Demo script showing how Room Selection and Additional Services are displayed
in the booking summary feature.
"""

def display_room_selection_demo():
    """Demo of Room Selection display"""
    print("=== Room Selection Demo ===")
    print("This section shows selected rooms with quantities and pricing:\n")
    
    # Sample room selection data
    rooms_selected = {
        "bedroom": {"quantity": 3, "price": 45.0},
        "bathroom": {"quantity": 2, "price": 30.0},
        "kitchen": {"quantity": 1, "price": 25.0},
        "living_room": {"quantity": 1, "price": 20.0}
    }
    
    print("Room Selection:")
    print("┌─────────────────────────────────────────────────┐")
    print("│ 🛏️  Bedroom    │ 3 rooms  │ $45.00              │")
    print("│ 🚿  Bathroom   │ 2 rooms  │ $30.00              │")
    print("│ 🍳  Kitchen    │ 1 room   │ $25.00              │")
    print("│ 🛋️  Living Room│ 1 room   │ $20.00              │")
    print("└─────────────────────────────────────────────────┘")
    print(f"Total Room Price: ${sum(room['price'] for room in rooms_selected.values()):.2f}\n")

def display_additional_services_demo():
    """Demo of Additional Services display"""
    print("=== Additional Services Demo ===")
    print("This section shows a la carte services separately:\n")
    
    # Sample additional services data
    a_la_carte_services = [
        {
            "name": "Inside Oven Cleaning",
            "description": "Deep cleaning of oven interior",
            "base_price": 35.0,
            "quantity": 1,
            "total_price": 35.0,
            "duration_hours": 1.0
        },
        {
            "name": "Refrigerator Cleaning",
            "description": "Interior and exterior cleaning",
            "base_price": 25.0,
            "quantity": 1,
            "total_price": 25.0,
            "duration_hours": 0.5
        },
        {
            "name": "Window Cleaning",
            "description": "Interior window cleaning",
            "base_price": 15.0,
            "quantity": 4,
            "total_price": 60.0,
            "duration_hours": 1.0
        }
    ]
    
    print("Additional Services:")
    print("┌─────────────────────────────────────────────────────────────────┐")
    for service in a_la_carte_services:
        print(f"│ 🔧 {service['name']:<20} │ {service['quantity']}x ${service['base_price']:.2f} │ ${service['total_price']:.2f} │")
        print(f"│    {service['description']:<52} │ {service['duration_hours']}h       │")
    print("└─────────────────────────────────────────────────────────────────┘")
    print(f"Total Additional Services: ${sum(service['total_price'] for service in a_la_carte_services):.2f}\n")

def display_services_booked_demo():
    """Demo of main Services Booked display"""
    print("=== Services Booked Demo ===")
    print("This section shows main cleaning services:\n")
    
    # Sample main services data
    services_booked = [
        {
            "name": "Standard House Cleaning",
            "description": "Comprehensive cleaning of all rooms",
            "base_price": 120.0,
            "quantity": 1,
            "total_price": 120.0,
            "duration_hours": 3.0
        }
    ]
    
    print("Services Booked:")
    print("┌─────────────────────────────────────────────────────────────────┐")
    for service in services_booked:
        print(f"│ 🏠 {service['name']:<20} │ {service['quantity']}x ${service['base_price']:.2f} │ ${service['total_price']:.2f} │")
        print(f"│    {service['description']:<52} │ {service['duration_hours']}h       │")
    print("└─────────────────────────────────────────────────────────────────┘\n")

def display_complete_summary_demo():
    """Demo of complete booking summary"""
    print("=== Complete Booking Summary Demo ===")
    print("Shows how all sections work together:\n")
    
    # Sample pricing breakdown
    pricing_breakdown = {
        "base_price": 120.0,
        "room_price": 120.0,
        "a_la_carte_total": 120.0,
        "subtotal": 360.0,
        "discount_amount": 36.0,
        "final_total": 324.0
    }
    
    print("Complete Checkout Summary:")
    print("=" * 60)
    
    # Services Booked
    print("📋 Services Selected:")
    print("   • Standard House Cleaning - $120.00 (3h)")
    
    # Room Selection
    print("\n🏠 Room Selection:")
    print("   • Bedroom (3) - $45.00")
    print("   • Bathroom (2) - $30.00") 
    print("   • Kitchen (1) - $25.00")
    print("   • Living Room (1) - $20.00")
    
    # Additional Services
    print("\n🔧 Additional Services:")
    print("   • Inside Oven Cleaning - $35.00 (1h)")
    print("   • Refrigerator Cleaning - $25.00 (0.5h)")
    print("   • Window Cleaning (4) - $60.00 (1h)")
    
    # Pricing Breakdown
    print("\n💰 Pricing Breakdown:")
    print("   Base Service Price:        $120.00")
    print("   Room Selection Price:      $120.00")
    print("   Additional Services:       $120.00")
    print("   ──────────────────────────────────")
    print("   Subtotal:                 $360.00")
    print("   Discount (10%):           -$36.00")
    print("   ──────────────────────────────────")
    print("   Final Total:              $324.00")
    print("=" * 60)

def main():
    """Main demo function"""
    print("🎉 Booking Summary Feature Demo")
    print("=" * 50)
    print("This demo shows how Room Selection and Additional Services")
    print("are displayed in the comprehensive booking summary.\n")
    
    display_room_selection_demo()
    display_additional_services_demo()
    display_services_booked_demo()
    display_complete_summary_demo()
    
    print("✅ Feature Implementation Complete!")
    print("\n🔧 Backend: Provides comprehensive summary with room_selection and a_la_carte_services")
    print("🎨 Frontend: Displays sections with proper formatting and pricing")
    print("📱 Responsive: Works on mobile and desktop")
    print("🔄 Fallback: Graceful degradation if summary endpoint unavailable")

if __name__ == "__main__":
    main()
