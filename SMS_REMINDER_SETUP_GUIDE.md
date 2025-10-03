# SMS Reminder System Setup Guide

## Overview
This guide will help you set up the customizable text message reminder system for your cleaning service booking platform. The system integrates with Twilio to send automated and manual SMS reminders to customers.

## Features
- **Customizable Templates**: Create and manage SMS reminder templates
- **Automatic Scheduling**: Send reminders automatically based on booking dates
- **Manual Sending**: Send immediate reminders for specific bookings
- **Admin Interface**: Full management interface for templates and settings
- **Customer Status**: Customers can view reminder status in their dashboard
- **Comprehensive Logging**: Track all sent reminders and their status

## Prerequisites
1. Twilio account with SMS capabilities
2. Twilio phone number
3. Backend server running
4. Frontend application running

## Backend Setup

### 1. Install Dependencies
The system requires the Twilio Python SDK. Install it by running:
```bash
cd backend
pip install twilio>=8.10.0
```

### 2. Environment Configuration
Add the following environment variables to your `.env` file:

```env
# Twilio SMS Configuration
TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_PHONE_NUMBER=your_twilio_phone_number_here
```

### 3. Get Twilio Credentials
1. Sign up for a Twilio account at https://www.twilio.com
2. Go to the Twilio Console Dashboard
3. Copy your Account SID and Auth Token
4. Purchase a phone number from Twilio (required for sending SMS)
5. Update your `.env` file with these credentials

### 4. Database Collections
The system will automatically create the following MongoDB collections:
- `reminder_templates`: Stores SMS template configurations
- `reminder_logs`: Tracks all sent reminders and their status

## Frontend Setup

### 1. Import Components
The SMS reminder management is integrated into the Admin Dashboard. No additional setup is required.

### 2. Customer Dashboard Integration
To show reminder status to customers, import and use the `ReminderStatus` component:

```jsx
import ReminderStatus from './components/ReminderStatus';

// In your customer dashboard
<ReminderStatus bookingId={booking.id} />
```

## Default Templates

The system comes with pre-configured templates:

### 1. Booking Confirmation
- **Type**: `booking_confirmation`
- **Timing**: Immediate
- **Template**: "Hi {customer_name}! Your cleaning service is confirmed for {booking_date} at {time_slot}. We'll see you soon! - Maids of CyFair"

### 2. Day Before Reminder
- **Type**: `day_before_reminder`
- **Timing**: 24 hours before
- **Template**: "Reminder: Your cleaning service is tomorrow ({booking_date}) at {time_slot}. Please ensure access to your home. - Maids of CyFair"

### 3. Hour Before Reminder
- **Type**: `hour_before_reminder`
- **Timing**: 1 hour before
- **Template**: "Your cleaner will arrive in about 1 hour for your {booking_date} service. Please ensure access to your home. - Maids of CyFair"

### 4. Cleaner On The Way
- **Type**: `cleaner_on_the_way`
- **Timing**: Immediate
- **Template**: "Your cleaner is on the way! ETA: {eta}. Please ensure access to your home. - Maids of CyFair"

### 5. Service Completed
- **Type**: `service_completed`
- **Timing**: Immediate
- **Template**: "Thank you for choosing Maids of CyFair! Your cleaning service is complete. We hope you're satisfied with our work. - Maids of CyFair"

## Template Variables

You can use the following variables in your templates:
- `{customer_name}`: Customer's first and last name
- `{booking_date}`: Formatted booking date
- `{time_slot}`: Booking time slot
- `{house_size}`: House size (small, medium, large)
- `{services}`: List of selected services
- `{eta}`: Estimated arrival time
- `{company_name}`: Your company name

## API Endpoints

### Template Management
- `GET /api/reminder-templates` - Get all templates
- `GET /api/reminder-templates/{id}` - Get specific template
- `POST /api/reminder-templates` - Create new template (admin only)
- `PUT /api/reminder-templates/{id}` - Update template (admin only)
- `DELETE /api/reminder-templates/{id}` - Delete template (admin only)

### Reminder Sending
- `POST /api/reminders/send` - Send manual reminder
- `POST /api/reminders/send-immediate` - Send immediate reminder
- `GET /api/reminders/logs` - Get reminder logs
- `GET /api/reminders/sms-status` - Check SMS service status

### Scheduler Management
- `POST /api/reminders/scheduler/start` - Start automatic scheduler (admin only)
- `POST /api/reminders/scheduler/stop` - Stop automatic scheduler (admin only)
- `GET /api/reminders/scheduler/status` - Get scheduler status

## Usage Guide

### For Administrators

1. **Access SMS Management**
   - Go to Admin Dashboard
   - Click on the "SMS" tab
   - View SMS configuration status

2. **Manage Templates**
   - View all existing templates
   - Create new custom templates
   - Edit existing templates
   - Delete unused templates

3. **Send Manual Reminders**
   - Use the "Send Manual Reminder" feature
   - Select booking ID and template
   - Optionally override with custom message

4. **Monitor Reminder Logs**
   - View all sent reminders
   - Check delivery status
   - Track failed deliveries

5. **Control Scheduler**
   - Start/stop automatic reminder scheduler
   - Monitor scheduler status
   - Configure reminder timing

### For Customers

1. **View Reminder Status**
   - Check reminder status in customer dashboard
   - See when reminders were sent
   - View delivery confirmation

## Automatic Reminder Flow

1. **Booking Confirmation**: Sent immediately when booking is created
2. **Day Before Reminder**: Sent 24 hours before service date
3. **Hour Before Reminder**: Sent 1 hour before service time
4. **Cleaner On The Way**: Sent when cleaner starts heading to location
5. **Service Completed**: Sent after service completion

## Troubleshooting

### Common Issues

1. **SMS Not Sending**
   - Check Twilio credentials in `.env` file
   - Verify phone number format (include country code)
   - Check Twilio account balance
   - Review error logs in reminder_logs collection

2. **Templates Not Loading**
   - Ensure database connection is working
   - Check if default templates were initialized
   - Verify admin permissions

3. **Scheduler Not Running**
   - Check if scheduler is started
   - Review server logs for errors
   - Verify database connectivity

### Debug Steps

1. **Check SMS Status**
   ```bash
   curl -X GET "http://localhost:8000/api/reminders/sms-status"
   ```

2. **Test Manual Send**
   - Use admin interface to send test reminder
   - Check reminder logs for status
   - Verify Twilio webhook delivery

3. **Review Logs**
   - Check server logs for errors
   - Review MongoDB reminder_logs collection
   - Monitor Twilio console for delivery status

## Security Considerations

1. **API Authentication**: All admin endpoints require authentication
2. **Phone Number Validation**: System validates phone number format
3. **Rate Limiting**: Consider implementing rate limiting for SMS sending
4. **Data Privacy**: Reminder logs contain customer phone numbers - ensure GDPR compliance

## Cost Management

1. **Twilio Pricing**: SMS costs vary by country (typically $0.0075 per SMS in US)
2. **Template Optimization**: Keep messages concise to reduce costs
3. **Delivery Tracking**: Monitor failed deliveries to avoid unnecessary retries
4. **Scheduling**: Use appropriate timing to avoid spam complaints

## Best Practices

1. **Message Content**
   - Keep messages concise and professional
   - Include company name for branding
   - Use clear, actionable language
   - Avoid excessive frequency

2. **Timing**
   - Send confirmations immediately
   - Send reminders at appropriate intervals
   - Respect customer time zones
   - Avoid sending during late hours

3. **Template Management**
   - Test templates before deployment
   - Keep backup of working templates
   - Regular review and updates
   - A/B test different messages

## Support

For technical support:
1. Check this guide first
2. Review server logs
3. Test with Twilio console
4. Contact development team

For Twilio-specific issues:
1. Check Twilio documentation
2. Review Twilio console logs
3. Contact Twilio support

## Future Enhancements

Potential improvements:
1. **Two-way SMS**: Allow customers to reply to reminders
2. **Opt-out Management**: Handle unsubscribe requests
3. **Delivery Reports**: Detailed delivery analytics
4. **Template A/B Testing**: Test different message variations
5. **International Support**: Multi-language templates
6. **Rich Media**: Support for MMS messages
7. **Integration**: Connect with other communication channels
