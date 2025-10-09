#!/usr/bin/env python3
"""
Test Amazon SES Configuration
"""
import os
import sys
sys.path.append('backend')

from backend.services.email_service import EmailService

def test_ses_configuration():
    """Test SES configuration and send a test email"""
    print("🔍 Testing Amazon SES Configuration...")
    
    # Check environment variables
    required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_REGION', 'FROM_EMAIL']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file in the backend directory.")
        return False
    
    print("✅ All required environment variables are set")
    
    # Test SES connection
    try:
        email_service = EmailService()
        print("✅ SES client initialized successfully")
        
        # Test sending email (replace with your verified email)
        test_email = input("Enter your verified email address for testing: ")
        
        if not test_email:
            print("❌ No email provided for testing")
            return False
        
        success = email_service.send_email(
            to_email=test_email,
            subject="SES Test Email - Maids of CyFair",
            html_content="""
            <html>
                <body>
                    <h2>🎉 SES Configuration Successful!</h2>
                    <p>Your Amazon SES is working correctly.</p>
                    <p>This email was sent from your Maids of CyFair application.</p>
                </body>
            </html>
            """,
            text_content="SES Configuration Successful! Your Amazon SES is working correctly."
        )
        
        if success:
            print("✅ Test email sent successfully!")
            print(f"📧 Check your inbox at: {test_email}")
            return True
        else:
            print("❌ Failed to send test email")
            return False
            
    except Exception as e:
        print(f"❌ Error testing SES: {e}")
        return False

if __name__ == "__main__":
    test_ses_configuration()
