#!/usr/bin/env python3
"""
Test script to verify Facebook URL appears in invoice PDF
"""

import requests
import base64
import json
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@maids.com"
ADMIN_PASSWORD = "admin123"

def test_invoice_generation():
    """Test invoice generation and check for Facebook URL"""
    
    print("🔍 Testing Invoice Generation with Facebook URL...")
    
    # Step 1: Login as admin
    print("\n1. Logging in as admin...")
    login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
        return False
    
    admin_token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {admin_token}"}
    print("✅ Admin login successful")
    
    # Step 2: Get existing bookings
    print("\n2. Getting existing bookings...")
    bookings_response = requests.get(f"{BASE_URL}/api/admin/bookings", headers=headers)
    
    if bookings_response.status_code != 200:
        print(f"❌ Failed to get bookings: {bookings_response.status_code}")
        return False
    
    bookings = bookings_response.json()
    print(f"✅ Found {len(bookings)} bookings")
    
    if not bookings:
        print("❌ No bookings found to generate invoice")
        return False
    
    # Step 3: Check for existing invoices first
    print("\n3. Checking for existing invoices...")
    invoices_response = requests.get(f"{BASE_URL}/api/admin/invoices", headers=headers)
    
    if invoices_response.status_code != 200:
        print(f"❌ Failed to get invoices: {invoices_response.status_code}")
        return False
    
    invoices = invoices_response.json()
    print(f"✅ Found {len(invoices)} existing invoices")
    
    if not invoices:
        print("❌ No existing invoices found")
        return False
    
    # Use the first existing invoice
    invoice = invoices[0]
    print(f"✅ Using existing invoice: {invoice['invoice_number']}")
    
    # Step 4: Generate PDF
    print(f"\n4. Generating PDF for invoice {invoice['id']}...")
    pdf_response = requests.get(
        f"{BASE_URL}/api/admin/invoices/{invoice['id']}/pdf",
        headers=headers
    )
    
    if pdf_response.status_code != 200:
        print(f"❌ Failed to generate PDF: {pdf_response.status_code}")
        print(pdf_response.text)
        return False
    
    pdf_data = pdf_response.json()
    print("✅ PDF generated successfully")
    
    # Step 5: Decode and check PDF content
    print("\n5. Checking PDF content for Facebook URL...")
    try:
        pdf_content = base64.b64decode(pdf_data["pdf_content"])
        
        # Check if Facebook URL is in the PDF content
        pdf_text = pdf_content.decode('utf-8', errors='ignore')
        
        facebook_url = "https://www.facebook.com/people/Maids-of-Cy-Fair/61551869414470/"
        if facebook_url in pdf_text:
            print("✅ Facebook URL found in PDF content!")
            print(f"   Found: {facebook_url}")
        else:
            print("❌ Facebook URL NOT found in PDF content")
            print("   PDF content preview:")
            print(pdf_text[:500] + "..." if len(pdf_text) > 500 else pdf_text)
            
        # Also check for "Follow us on Facebook"
        if "Follow us on Facebook" in pdf_text:
            print("✅ 'Follow us on Facebook' text found in PDF!")
        else:
            print("❌ 'Follow us on Facebook' text NOT found in PDF")
            
    except Exception as e:
        print(f"❌ Error checking PDF content: {e}")
        return False
    
    print(f"\n📄 PDF filename: {pdf_data.get('filename', 'unknown')}")
    print("✅ Test completed!")
    return True

if __name__ == "__main__":
    test_invoice_generation()
