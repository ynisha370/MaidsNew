#!/usr/bin/env python3
"""
Simple test to trigger PDF generation and check for debug output
"""

import requests
import json

# Test configuration
BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@maids.com"
ADMIN_PASSWORD = "admin123"

def test_pdf_generation():
    """Test PDF generation and check for debug output"""
    
    print("🔍 Testing PDF Generation with Debug Output...")
    
    # Step 1: Login as admin
    print("\n1. Logging in as admin...")
    login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
    
    admin_token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {admin_token}"}
    print("✅ Admin login successful")
    
    # Step 2: Get existing invoices
    print("\n2. Getting existing invoices...")
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
    
    # Step 3: Generate PDF
    print(f"\n3. Generating PDF for invoice {invoice['id']}...")
    print("   (Check server logs for 'DEBUG: Added Facebook URL to PDF' message)")
    
    pdf_response = requests.get(
        f"{BASE_URL}/api/admin/invoices/{invoice['id']}/pdf",
        headers=headers
    )
    
    if pdf_response.status_code != 200:
        print(f"❌ Failed to generate PDF: {pdf_response.status_code}")
        print(pdf_response.text)
        return False
    
    print("✅ PDF generated successfully")
    print("   If you see 'DEBUG: Added Facebook URL to PDF' in server logs, the code is working")
    
    return True

if __name__ == "__main__":
    test_pdf_generation()
