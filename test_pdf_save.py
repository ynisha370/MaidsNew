#!/usr/bin/env python3
"""
Test to save PDF and examine its content
"""

import requests
import base64
import os

# Test configuration
BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@maids.com"
ADMIN_PASSWORD = "admin123"

def test_pdf_save():
    """Test PDF generation and save to file"""
    
    print("🔍 Testing PDF Generation and Saving...")
    
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
        
        filename = f"test_invoice_{invoice['invoice_number']}.pdf"
        with open(filename, 'wb') as f:
            f.write(pdf_content)
        
        print(f"✅ PDF saved as: {filename}")
        print(f"   File size: {len(pdf_content)} bytes")
        
        # Check if Facebook URL is in the PDF content
        pdf_text = pdf_content.decode('utf-8', errors='ignore')
        
        facebook_url = "https://www.facebook.com/people/Maids-of-Cy-Fair/61551869414470/"
        if facebook_url in pdf_text:
            print("✅ Facebook URL found in PDF content!")
        else:
            print("❌ Facebook URL NOT found in PDF content")
            
        if "Follow us on Facebook" in pdf_text:
            print("✅ 'Follow us on Facebook' text found in PDF!")
        else:
            print("❌ 'Follow us on Facebook' text NOT found in PDF")
            
        # Show first 1000 characters of PDF text
        print(f"\n📄 PDF text preview (first 1000 chars):")
        print(pdf_text[:1000])
        
    except Exception as e:
        print(f"❌ Error saving PDF: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_pdf_save()
