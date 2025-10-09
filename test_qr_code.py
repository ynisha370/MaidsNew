#!/usr/bin/env python3
"""
Test QR code generation for invoice
"""

import requests
import base64
import os

# Test configuration
BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@maids.com"
ADMIN_PASSWORD = "admin123"

def test_qr_code_generation():
    """Test QR code generation in invoice PDF"""
    
    print("🔍 Testing QR Code Generation in Invoice...")
    
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
    print("   (Check server logs for QR code debug messages)")
    
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
    
    # Step 4: Save PDF to file
    print("\n4. Saving PDF to file...")
    try:
        pdf_content = base64.b64decode(pdf_data["pdf_content"])
        
        filename = f"test_invoice_with_qr_{invoice['invoice_number']}.pdf"
        with open(filename, 'wb') as f:
            f.write(pdf_content)
        
        print(f"✅ PDF saved as: {filename}")
        print(f"   File size: {len(pdf_content)} bytes")
        
        # Check if QR code related text is in the PDF content
        pdf_text = pdf_content.decode('utf-8', errors='ignore')
        
        if "Scan QR code" in pdf_text:
            print("✅ 'Scan QR code' text found in PDF!")
        else:
            print("❌ 'Scan QR code' text NOT found in PDF")
            
        if "Facebook" in pdf_text:
            print("✅ 'Facebook' text found in PDF!")
        else:
            print("❌ 'Facebook' text NOT found in PDF")
            
        # Show first 1000 characters of PDF text
        print(f"\n📄 PDF text preview (first 1000 chars):")
        print(pdf_text[:1000])
        
    except Exception as e:
        print(f"❌ Error saving PDF: {e}")
        return False
    
    print("\n✅ QR Code test completed!")
    print("   If you see 'DEBUG: Added QR code to PDF' in server logs, the QR code was added successfully")
    return True

if __name__ == "__main__":
    test_qr_code_generation()
