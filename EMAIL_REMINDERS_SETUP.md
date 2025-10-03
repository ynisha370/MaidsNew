# Email Reminders Setup Guide

## Overview
This guide will help you set up Amazon SES integration for sending automated email reminders to your customers about their upcoming cleaning appointments.

## Features Implemented

### 📧 Email Reminder System
- **Dynamic Email Templates**: Beautiful, responsive HTML email templates with your branding
- **Batch Email Sending**: Send reminders to multiple customers at once
- **Multiple Reminder Types**: General, day-before, week-before, confirmation, and cancellation reminders
- **Admin Dashboard Integration**: Easy-to-use interface in your admin panel
- **Customer Data Integration**: Automatically pulls customer information from bookings

### 🎯 Admin Dashboard Features
- **Upcoming Bookings View**: See all bookings within a specified time period
- **Bulk Selection**: Select multiple bookings for batch email sending
- **Email Status Tracking**: See which customers have valid email addresses
- **Reminder Type Selection**: Choose the appropriate reminder type for each batch
- **Send Results**: Get detailed feedback on email delivery success/failure

## Setup Instructions

### 1. AWS SES Configuration

#### Step 1: Create AWS Account
1. Go to [AWS Console](https://console.aws.amazon.com/)
2. Create an AWS account if you don't have one
3. Navigate to Amazon SES service

#### Step 2: Verify Email Domain
1. In SES console, go to "Verified identities"
2. Click "Create identity"
3. Choose "Domain" and enter your domain (e.g., `maidsofcyfair.com`)
4. Follow the DNS verification process
5. Wait for verification (can take up to 72 hours)

#### Step 3: Create IAM User for SES
1. Go to IAM service in AWS Console
2. Create a new user with programmatic access
3. Attach the `AmazonSESFullAccess` policy
4. Save the Access Key ID and Secret Access Key

#### Step 4: Request Production Access (Optional)
- By default, SES is in sandbox mode (can only send to verified emails)
- To send to any email address, request production access
- Go to SES console → Account dashboard → Request production access

### 2. Environment Configuration

#### Backend Environment Variables
Add these variables to your `.env` file in the backend directory:

```bash
# AWS SES Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key_id_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key_here
AWS_REGION=us-east-1
FROM_EMAIL=noreply@maidsofcyfair.com
FROM_NAME=Maids of CyFair
```

#### Frontend Environment Variables
No additional frontend configuration needed - the email reminders are integrated into the existing admin dashboard.

### 3. Install Dependencies

The required dependencies are already included in `requirements.txt`:
- `boto3>=1.34.129` - AWS SDK for Python

Install them with:
```bash
cd backend
pip install -r requirements.txt
```

### 4. Database Setup

No additional database setup required - the email reminders use existing booking and user data.

## Usage Guide

### Accessing Email Reminders
1. Log into your admin dashboard
2. Navigate to the "Email" tab (new tab in the admin interface)
3. You'll see the Email Reminders interface

### Sending Individual Reminders
1. Select a booking from the upcoming bookings list
2. Click "Send Reminder" for that specific booking
3. The system will automatically send a personalized email

### Sending Batch Reminders
1. Use the checkboxes to select multiple bookings
2. Choose the appropriate reminder type from the dropdown
3. Click "Send to X Selected" to send batch emails
4. Monitor the results in the email stats section

### Reminder Types
- **General Reminder**: Standard appointment reminder
- **Day Before**: Reminder sent the day before the appointment
- **Week Before**: Reminder sent a week before the appointment
- **Confirmation**: Confirmation email for new bookings
- **Cancellation**: Notification for cancelled appointments

## Email Template Features

### Professional Design
- Responsive HTML design that works on all devices
- Your company branding and colors
- Professional layout with clear appointment details

### Dynamic Content
- Customer's name and appointment details
- Date, time, and location information
- Total amount and service details
- Contact information for questions

### Email Content Includes
- Appointment date and time
- Service address
- Total amount
- What to expect instructions
- Contact information
- Professional footer

## API Endpoints

The following API endpoints are available for email reminders:

### Send Single Reminder
```
POST /api/admin/email-reminders/send-single
```
**Body:**
```json
{
  "booking_id": "booking-uuid",
  "reminder_type": "upcoming"
}
```

### Send Batch Reminders
```
POST /api/admin/email-reminders/send-batch
```
**Body:**
```json
{
  "booking_ids": ["booking-uuid-1", "booking-uuid-2"],
  "reminder_type": "upcoming"
}
```

### Get Upcoming Bookings
```
GET /api/admin/email-reminders/upcoming?days_ahead=7
```

## Troubleshooting

### Common Issues

#### 1. Emails Not Sending
- Check AWS credentials in environment variables
- Verify your domain is verified in SES
- Check AWS SES sending limits
- Ensure you're not in sandbox mode (if sending to unverified emails)

#### 2. "No Email Available" Status
- This means the customer doesn't have an email address in the system
- Check if the booking was made by a guest user
- Verify the user's email in the user management section

#### 3. AWS SES Errors
- Check AWS CloudWatch logs for detailed error messages
- Verify IAM permissions for the SES user
- Ensure the region matches your SES setup

### Debugging Steps
1. Check the backend logs for error messages
2. Verify AWS credentials are correct
3. Test with a single email first
4. Check SES console for bounce/complaint rates

## Security Considerations

### AWS Security
- Use IAM roles with minimal required permissions
- Rotate access keys regularly
- Monitor SES usage and costs
- Set up CloudWatch alarms for unusual activity

### Email Security
- Never hardcode credentials in the code
- Use environment variables for all sensitive data
- Implement rate limiting for email sending
- Monitor bounce and complaint rates

## Cost Considerations

### AWS SES Pricing
- First 62,000 emails per month are free (if sent from EC2)
- After that: $0.10 per 1,000 emails
- Additional charges for attachments or data transfer

### Optimization Tips
- Use batch sending to reduce API calls
- Implement email validation before sending
- Monitor bounce rates to maintain good sender reputation
- Use appropriate reminder timing to avoid spam complaints

## Future Enhancements

### Planned Features
- **Automated Scheduling**: Set up automatic reminders based on appointment dates
- **Email Templates**: Customizable email templates in the admin interface
- **Email Analytics**: Track open rates and click-through rates
- **A/B Testing**: Test different email templates for better engagement
- **SMS Integration**: Combine email and SMS reminders
- **Customer Preferences**: Let customers choose their preferred reminder method

### Integration Opportunities
- **Calendar Integration**: Sync with Google Calendar for automatic reminders
- **CRM Integration**: Connect with customer relationship management systems
- **Marketing Automation**: Use for promotional emails and newsletters
- **Feedback Collection**: Include customer satisfaction surveys in emails

## Support

For technical support or questions about the email reminder system:
1. Check the troubleshooting section above
2. Review AWS SES documentation
3. Contact your development team
4. Check the application logs for detailed error messages

## Conclusion

The email reminder system provides a professional way to communicate with your customers about their cleaning appointments. With proper AWS SES setup and configuration, you can send beautiful, personalized emails that enhance your customer experience and reduce no-shows.

Remember to:
- Test thoroughly before going live
- Monitor email delivery rates
- Keep your AWS credentials secure
- Regularly review and update email templates
- Monitor customer feedback and engagement
