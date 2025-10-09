# Amazon SES Email Verification Guide

## Issue: Email Address Not Verified

Your Amazon SES account is in **sandbox mode**, which means you can only send emails to verified email addresses.

**Error**: `Email address is not verified. The following identities failed the check in region US-EAST-1: nitin23359@iiit.ac.in`

## Solution: Verify Email Address in AWS SES Console

### Step 1: Access AWS SES Console
1. Go to [AWS Console](https://console.aws.amazon.com/)
2. Navigate to **Services** → **Simple Email Service (SES)**
3. Make sure you're in the **US East (N. Virginia)** region (us-east-1)

### Step 2: Verify Email Address
1. In the SES console, click **"Verified identities"** in the left sidebar
2. Click **"Create identity"**
3. Select **"Email address"**
4. Enter: `nitin23359@iiit.ac.in`
5. Click **"Create identity"**

### Step 3: Check Email for Verification
1. Check the inbox of `nitin23359@iiit.ac.in`
2. Look for an email from AWS with subject: "Amazon SES Email Address Verification Request"
3. Click the verification link in the email
4. You should see a success message

### Step 4: Test Email Again
After verification, run the test again:
```bash
python3 send_test_email.py
```

## Alternative: Request Production Access

If you want to send emails to any address (not just verified ones):

### Step 1: Request Production Access
1. In SES console, go to **"Account dashboard"**
2. Click **"Request production access"**
3. Fill out the form:
   - **Mail type**: Transactional
   - **Website URL**: Your website URL
   - **Use case description**: "Sending booking confirmations and appointment reminders for a cleaning service business"
   - **Bounce and complaint handling**: Yes
   - **Sending statistics**: Provide your expected volume
4. Submit the request

### Step 2: Wait for Approval
- Usually takes 24-48 hours
- AWS will review your request
- You'll receive an email when approved

## Current Status
- ✅ SES is working correctly
- ✅ Can send to verified emails (ynitin370@gmail.com)
- ❌ Cannot send to unverified emails (nitin23359@iiit.ac.in)
- 🔄 Need to verify email or request production access

## Quick Fix Options

### Option 1: Verify the Email (Recommended)
- Fastest solution
- Takes 2-3 minutes
- Just verify `nitin23359@iiit.ac.in` in SES console

### Option 2: Use Verified Email for Testing
- Send test emails to `ynitin370@gmail.com` (already verified)
- This works immediately

### Option 3: Request Production Access
- Allows sending to any email address
- Takes 24-48 hours for approval
- Required for production use

## Next Steps
1. **Immediate**: Verify `nitin23359@iiit.ac.in` in AWS SES console
2. **Then**: Run the test email script again
3. **Future**: Request production access for full functionality
