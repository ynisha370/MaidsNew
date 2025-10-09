#!/usr/bin/env python3
"""
Test Automated Reminder System
"""
import os
import sys
sys.path.append('backend')

from backend.services.email_service import EmailService
from datetime import datetime, timedelta

def test_reminder_system():
    """Test the automated reminder system"""
    print("🔍 Testing Automated Reminder System...")
    
    # Initialize email service
    email_service = EmailService()
    
    # Create sample booking data
    sample_booking = {
        'id': 'test_booking_123',
        'customer': {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'ynitin370@gmail.com'
        },
        'booking_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
        'time_slot': '10:00 AM - 12:00 PM',
        'total_amount': 150.00,
        'address': {
            'street': '123 Main Street',
            'city': 'Houston',
            'state': 'TX',
            'zip_code': '77001'
        },
        'house_size': '3 Bedroom',
        'frequency': 'One-time'
    }
    
    print("📅 Testing booking reminder email...")
    
    # Test booking reminder
    success = email_service.send_booking_reminder(sample_booking, "upcoming")
    
    if success:
        print("✅ Booking reminder sent successfully!")
    else:
        print("❌ Failed to send booking reminder")
        return False
    
    print("\n👥 Testing cleaner approval email...")
    
    # Test cleaner approval email
    success = email_service.send_cleaner_approved_email(
        cleaner_email="ynitin370@gmail.com",
        cleaner_name="Jane Smith",
        login_url="http://localhost:3000/cleaner-login"
    )
    
    if success:
        print("✅ Cleaner approval email sent successfully!")
    else:
        print("❌ Failed to send cleaner approval email")
        return False
    
    print("\n📋 Testing job assignment email...")
    
    # Test job assignment email
    job_details = {
        'booking_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
        'time_slot': '10:00 AM - 12:00 PM',
        'house_size': '3 Bedroom',
        'frequency': 'One-time',
        'total_amount': 150.00,
        'address_text': '123 Main Street, Houston, TX 77001'
    }
    
    success = email_service.send_job_assigned_email(
        cleaner_email="ynitin370@gmail.com",
        cleaner_name="Jane Smith",
        job_details=job_details
    )
    
    if success:
        print("✅ Job assignment email sent successfully!")
    else:
        print("❌ Failed to send job assignment email")
        return False
    
    print("\n🎉 All reminder system tests completed!")
    print("📧 Check your inbox for all test emails")
    
    return True

if __name__ == "__main__":
    test_reminder_system()
