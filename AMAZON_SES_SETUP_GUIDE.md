# Amazon SES Setup Guide

## Overview
This guide will help you set up Amazon SES (Simple Email Service) for your Maids of CyFair application to send automated email reminders and notifications.

## Prerequisites
- AWS Account (free tier available)
- Domain name (for production) or verified email address (for testing)
- Access to your project's backend environment

---

## Step 1: Create AWS Account and Access Keys

### 1.1 Create AWS Account
1. Go to [AWS Console](https://aws.amazon.com/)
2. Click "Create an AWS Account"
3. Follow the signup process (free tier available)

### 1.2 Create IAM User for SES
1. **Navigate to IAM:**
   - Go to AWS Console → Services → IAM
   - Click "Users" → "Create user"

2. **User Details:**
   - Username: `maids-ses-user`
   - Select "Programmatic access"

3. **Attach Policies:**
   - Click "Attach existing policies directly"
   - Search and select: `AmazonSESFullAccess`
   - Click "Next" → "Create user"

4. **Save Credentials:**
   - **IMPORTANT**: Copy and save these credentials securely:
     - Access Key ID
     - Secret Access Key
   - You won't be able to see the secret key again!

---

## Step 2: Set Up Amazon SES

### 2.1 Navigate to SES
1. Go to AWS Console → Services → Simple Email Service (SES)
2. Select your preferred region (e.g., `us-east-1`)

### 2.2 Verify Email Address (For Testing)
1. **Click "Verified identities"** in the left sidebar
2. **Click "Create identity"**
3. **Select "Email address"**
4. **Enter your email** (e.g., `your-email@example.com`)
5. **Click "Create identity"**
6. **Check your email** and click the verification link

### 2.3 Verify Domain (For Production)
1. **Click "Create identity"**
2. **Select "Domain"**
3. **Enter your domain** (e.g., `maidsofcyfair.com`)
4. **Configure DNS records** as instructed by AWS
5. **Wait for verification** (can take up to 72 hours)

---

## Step 3: Configure SES Settings

### 3.1 Request Production Access (If Needed)
- **Sandbox Mode**: Can only send to verified email addresses
- **Production Mode**: Can send to any email address
- **To request production access:**
  1. Go to SES → Account dashboard
  2. Click "Request production access"
  3. Fill out the form with your use case
  4. Wait for approval (usually 24-48 hours)

### 3.2 Configure Sending Statistics
1. Go to SES → Account dashboard
2. Review your sending limits
3. Request limit increases if needed

---

## Step 4: Update Your Application Configuration

### 4.1 Create Backend .env File
Create a `.env` file in your `backend/` directory:

```bash
# AWS SES Configuration
AWS_ACCESS_KEY_ID=your_actual_access_key_here
AWS_SECRET_ACCESS_KEY=your_actual_secret_key_here
AWS_REGION=us-east-1
FROM_EMAIL=noreply@maidsofcyfair.com
FROM_NAME=Maids of CyFair

# Other existing configurations...
MONGO_URL=your_mongodb_url
JWT_SECRET=your_jwt_secret
# ... etc
```

### 4.2 Install Required Dependencies
Your project already has the required dependencies in `requirements.txt`:
- `boto3` (AWS SDK)
- `botocore` (AWS core library)

If not installed, run:
```bash
cd backend
pip install boto3 botocore
```

---

## Step 5: Test SES Configuration

### 5.1 Create Test Script
Create a test file `test_ses_setup.py` in your project root:

```python
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
```

### 5.2 Run the Test
```bash
cd /Users/nitinyadav/Documents/GitHub/MaidsNew
python test_ses_setup.py
```

---

## Step 6: Production Configuration

### 6.1 Update Email Templates
Your application already has comprehensive email templates in `email_service.py`:
- Booking reminders
- Cleaner approval notifications
- Job assignment emails
- Customer notifications

### 6.2 Configure Automated Reminders
The system includes automated reminder functionality:
- Day-before reminders
- Week-before reminders
- Custom reminder schedules

### 6.3 Set Up Monitoring
1. **CloudWatch Logs**: Monitor email sending
2. **SES Metrics**: Track bounce rates, complaints
3. **Set up alarms** for high bounce rates

---

## Step 7: Security Best Practices

### 7.1 IAM Permissions
- Use least privilege principle
- Create specific SES policies instead of full access
- Rotate access keys regularly

### 7.2 Email Security
- Always use HTTPS for email links
- Implement SPF, DKIM, and DMARC records
- Monitor bounce and complaint rates

### 7.3 Environment Variables
- Never commit `.env` files to version control
- Use AWS Secrets Manager for production
- Rotate credentials regularly

---

## Troubleshooting

### Common Issues

#### 1. "Email address not verified"
**Solution**: Verify the sender email address in SES console

#### 2. "Message rejected: Email address not verified"
**Solution**: Verify the recipient email address (in sandbox mode)

#### 3. "Access Denied"
**Solution**: Check IAM permissions and access keys

#### 4. "Region mismatch"
**Solution**: Ensure AWS_REGION matches your SES region

#### 5. "Rate limit exceeded"
**Solution**: Request limit increase in SES console

### Debug Steps
1. Check AWS credentials are correct
2. Verify email addresses are verified
3. Check SES region matches configuration
4. Review CloudWatch logs for detailed errors
5. Test with AWS CLI: `aws ses send-email --region us-east-1 --source your-email@domain.com --destination ToAddresses=test@example.com --message Subject={Data="Test"},Body={Text={Data="Test message"}}`

---

## Cost Information

### SES Pricing (as of 2024)
- **First 62,000 emails per month**: FREE
- **After free tier**: $0.10 per 1,000 emails
- **Data transfer**: $0.12 per GB

### Cost Optimization
- Use batch sending for multiple emails
- Implement proper bounce handling
- Monitor and maintain good sender reputation

---

## Next Steps

1. ✅ **Complete SES setup** following this guide
2. ✅ **Test email functionality** with the test script
3. ✅ **Configure production domain** verification
4. ✅ **Set up monitoring** and alerts
5. ✅ **Implement bounce handling** in your application
6. ✅ **Test automated reminders** with real bookings

---

## Support Resources

- [AWS SES Documentation](https://docs.aws.amazon.com/ses/)
- [SES Best Practices](https://docs.aws.amazon.com/ses/latest/dg/best-practices.html)
- [SES Troubleshooting](https://docs.aws.amazon.com/ses/latest/dg/troubleshooting.html)

---

**Status**: 🟡 Ready for configuration
**Estimated Time**: 30-45 minutes
**Priority**: HIGH - Required for email functionality
