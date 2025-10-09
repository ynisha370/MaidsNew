#!/usr/bin/env python3
"""
Test Amazon SES Configuration - Automated Version
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
    print(f"📧 From Email: {os.getenv('FROM_EMAIL')}")
    print(f"🌍 AWS Region: {os.getenv('AWS_REGION')}")
    
    # Test SES connection
    try:
        email_service = EmailService()
        print("✅ SES client initialized successfully")
        
        # Use the FROM_EMAIL as the test recipient (since it's verified)
        test_email = os.getenv('FROM_EMAIL')
        print(f"📧 Testing with verified email: {test_email}")
        
        success = email_service.send_email(
            to_email=test_email,
            subject="🎉 SES Test Email - Maids of CyFair",
            html_content="""
            <html>
                <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
                    <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                        <h2 style="color: #2c5aa0; text-align: center;">🎉 SES Configuration Successful!</h2>
                        <p>Your Amazon SES is working correctly with your Maids of CyFair application.</p>
                        
                        <div style="background-color: #e3f2fd; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <h3>✅ Configuration Details:</h3>
                            <ul>
                                <li><strong>AWS Region:</strong> us-east-1</li>
                                <li><strong>From Email:</strong> ynitin370@gmail.com</li>
                                <li><strong>Service:</strong> Amazon SES</li>
                                <li><strong>Status:</strong> Active and Ready</li>
                            </ul>
                        </div>
                        
                        <p>Your email system can now send:</p>
                        <ul>
                            <li>📅 Booking confirmation emails</li>
                            <li>⏰ Appointment reminders</li>
                            <li>👥 Cleaner notifications</li>
                            <li>📧 Customer communications</li>
                        </ul>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <p style="color: #4CAF50; font-weight: bold;">🚀 Email System Ready for Production!</p>
                        </div>
                        
                        <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e9ecef; color: #6c757d; font-size: 14px;">
                            <p>Maids of CyFair - Professional Cleaning Services</p>
                            <p>This is an automated test email from your application.</p>
                        </div>
                    </div>
                </body>
            </html>
            """,
            text_content="""
            🎉 SES Configuration Successful!
            
            Your Amazon SES is working correctly with your Maids of CyFair application.
            
            ✅ Configuration Details:
            - AWS Region: us-east-1
            - From Email: ynitin370@gmail.com
            - Service: Amazon SES
            - Status: Active and Ready
            
            Your email system can now send:
            - 📅 Booking confirmation emails
            - ⏰ Appointment reminders
            - 👥 Cleaner notifications
            - 📧 Customer communications
            
            🚀 Email System Ready for Production!
            
            Maids of CyFair - Professional Cleaning Services
            This is an automated test email from your application.
            """
        )
        
        if success:
            print("✅ Test email sent successfully!")
            print(f"📧 Check your inbox at: {test_email}")
            print("🎉 Your Amazon SES is working perfectly!")
            return True
        else:
            print("❌ Failed to send test email")
            return False
            
    except Exception as e:
        print(f"❌ Error testing SES: {e}")
        print("💡 Common issues:")
        print("   - Email address not verified in SES console")
        print("   - AWS credentials incorrect")
        print("   - SES region mismatch")
        print("   - Account in sandbox mode (can only send to verified emails)")
        return False

if __name__ == "__main__":
    test_ses_configuration()
