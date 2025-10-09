#!/usr/bin/env python3
"""
Send Test Email to ynitin370@gmail.com (Verified Email)
"""
import os
import sys
sys.path.append('backend')

from backend.services.email_service import EmailService

def send_test_email():
    """Send test email to ynitin370@gmail.com"""
    print("📧 Sending test email to ynitin370@gmail.com...")
    
    # Initialize email service
    email_service = EmailService()
    
    # Send test email
    success = email_service.send_email(
        to_email="ynitin370@gmail.com",
        subject="🎉 Test Email from Maids of CyFair - Amazon SES",
        html_content="""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <h2 style="color: #2c5aa0; text-align: center;">🎉 Amazon SES Test Email</h2>
                    <p>Hello from Maids of CyFair!</p>
                    
                    <div style="background-color: #e3f2fd; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3>✅ SES Configuration Successful!</h3>
                        <p>This email confirms that your Amazon SES is working perfectly with your Maids of CyFair application.</p>
                        
                        <ul>
                            <li><strong>From:</strong> ynitin370@gmail.com</li>
                            <li><strong>To:</strong> ynitin370@gmail.com (Verified Email)</li>
                            <li><strong>Service:</strong> Amazon SES</li>
                            <li><strong>Status:</strong> Active and Ready</li>
                            <li><strong>Mode:</strong> Sandbox (Verified emails only)</li>
                        </ul>
                    </div>
                    
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3>🚀 Your Email System Can Now Send:</h3>
                        <ul>
                            <li>📅 Booking confirmation emails</li>
                            <li>⏰ Appointment reminders</li>
                            <li>👥 Cleaner notifications</li>
                            <li>📧 Customer communications</li>
                            <li>🔄 Status updates</li>
                            <li>📊 Bulk marketing emails</li>
                        </ul>
                    </div>
                    
                    <div style="background-color: #fff3cd; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #ffc107;">
                        <h3>⚠️ Current Limitation:</h3>
                        <p><strong>Sandbox Mode:</strong> Can only send to verified email addresses</p>
                        <p><strong>To send to customers:</strong> Request production access in AWS SES console</p>
                        <p><strong>Time to approval:</strong> 24-48 hours</p>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <p style="color: #4CAF50; font-weight: bold; font-size: 18px;">🎉 Email System Ready for Production!</p>
                        <p>Your Maids of CyFair application is now fully equipped with professional email capabilities.</p>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e9ecef; color: #6c757d; font-size: 14px;">
                        <p><strong>Maids of CyFair</strong> - Professional Cleaning Services</p>
                        <p>This is a test email from your Amazon SES integration.</p>
                        <p>Email sent via Amazon SES from your application backend.</p>
                    </div>
                </div>
            </body>
        </html>
        """,
        text_content="""
        🎉 Amazon SES Test Email
        
        Hello from Maids of CyFair!
        
        ✅ SES Configuration Successful!
        This email confirms that your Amazon SES is working perfectly with your Maids of CyFair application.
        
        Details:
        - From: ynitin370@gmail.com
        - To: ynitin370@gmail.com (Verified Email)
        - Service: Amazon SES
        - Status: Active and Ready
        - Mode: Sandbox (Verified emails only)
        
        🚀 Your Email System Can Now Send:
        - 📅 Booking confirmation emails
        - ⏰ Appointment reminders
        - 👥 Cleaner notifications
        - 📧 Customer communications
        - 🔄 Status updates
        - 📊 Bulk marketing emails
        
        ⚠️ Current Limitation:
        Sandbox Mode: Can only send to verified email addresses
        To send to customers: Request production access in AWS SES console
        Time to approval: 24-48 hours
        
        🎉 Email System Ready for Production!
        Your Maids of CyFair application is now fully equipped with professional email capabilities.
        
        Maids of CyFair - Professional Cleaning Services
        This is a test email from your Amazon SES integration.
        Email sent via Amazon SES from your application backend.
        """
    )
    
    if success:
        print("✅ Test email sent successfully to ynitin370@gmail.com!")
        print("📧 Please check the inbox for the email")
        return True
    else:
        print("❌ Failed to send test email")
        return False

if __name__ == "__main__":
    send_test_email()
