#!/usr/bin/env python3
"""
Simple test to verify QR code generation works
"""

import qrcode
from io import BytesIO
from PIL import Image

def test_qr_generation():
    """Test QR code generation"""
    
    print("🔍 Testing QR Code Generation...")
    
    try:
        # Create QR code with Facebook URL
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data("https://www.facebook.com/people/Maids-of-Cy-Fair/61551869414470/")
        qr.make(fit=True)
        
        # Create QR code image
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to file
        qr_img.save("test_qr_code.png")
        print("✅ QR code generated successfully and saved as test_qr_code.png")
        
        # Check file size
        import os
        file_size = os.path.getsize("test_qr_code.png")
        print(f"   File size: {file_size} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating QR code: {e}")
        return False

if __name__ == "__main__":
    test_qr_generation()
