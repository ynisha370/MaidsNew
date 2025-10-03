# Google Calendar Integration Setup Guide

## Overview
This guide will help you set up Google Calendar integration for the Maids of Cyfair booking system, allowing cleaners to sync their schedules and automatically create calendar events for bookings.

## Prerequisites
- Google Cloud Console account
- Python 3.8+ installed
- MongoDB running
- Backend server running

## Step 1: Google Cloud Console Setup

### 1.1 Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your project ID

### 1.2 Enable Google Calendar API
1. In the Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Google Calendar API"
3. Click on it and press "Enable"

### 1.3 Create OAuth 2.0 Credentials
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Choose "Web application" as the application type
4. Set the name (e.g., "Maids of CyFair Calendar Integration")
5. Add authorized redirect URIs:
   - `http://localhost:8000/api/calendar/auth/callback` (for development)
   - `https://yourdomain.com/api/calendar/auth/callback` (for production)
6. Click "Create"
7. Download the JSON credentials file

## Step 2: Environment Configuration

### 2.1 Backend Environment Setup
Create or update your `.env` file in the backend directory:

```bash
# Google Calendar Configuration
GOOGLE_CLIENT_ID=your_google_client_id_from_console
GOOGLE_CLIENT_SECRET=your_google_client_secret_from_console
GOOGLE_REDIRECT_URI=http://localhost:8000/api/calendar/auth/callback
```

### 2.2 Install Dependencies
The required dependencies are already in `requirements.txt`:
- `google-api-python-client>=2.0.0`
- `google-auth>=2.0.0`
- `google-auth-oauthlib>=1.0.0`
- `google-auth-httplib2>=0.2.0`

Install them with:
```bash
cd backend
pip install -r requirements.txt
```

## Step 3: Google Calendar Scopes Configuration

The system is configured with the following scopes:
- `https://www.googleapis.com/auth/calendar.readonly` - Read calendar events
- `https://www.googleapis.com/auth/calendar.events` - Create, update, and delete calendar events

These scopes allow the system to:
- Read cleaner's existing calendar events
- Check availability
- Create new events for bookings
- Update event details
- Delete events when bookings are cancelled

## Step 4: API Endpoints

### 4.1 Calendar Authentication Endpoints

#### Get Authorization URL
```http
GET /api/calendar/auth/url
```
Returns the Google OAuth authorization URL for cleaners to authenticate.

#### Handle OAuth Callback
```http
POST /api/calendar/auth/callback
Content-Type: application/json

{
  "code": "authorization_code_from_google"
}
```
Exchanges the authorization code for access tokens and returns calendar credentials.

### 4.2 Calendar Management Endpoints

#### Setup Calendar Integration for Cleaner
```http
POST /api/admin/cleaners/{cleaner_id}/calendar/setup
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "credentials": {
    "token": "access_token",
    "refresh_token": "refresh_token",
    "client_id": "google_client_id",
    "client_secret": "google_client_secret",
    "scopes": ["calendar.readonly", "calendar.events"]
  },
  "calendar_id": "primary"
}
```

#### Get Cleaner Calendar Events
```http
GET /api/admin/cleaners/{cleaner_id}/calendar/events?days_ahead=7
Authorization: Bearer <admin_token>
```

#### Get Availability Summary
```http
GET /api/admin/calendar/availability-summary?date=2024-01-15
Authorization: Bearer <admin_token>
```

## Step 5: Frontend Integration

### 5.1 Calendar Integration Component
The system includes a `CalendarIntegration.js` component that provides:
- Cleaner selection dropdown
- Calendar ID input (defaults to 'primary')
- Credentials input field
- Setup button for calendar integration
- Calendar events display

### 5.2 Usage in Admin Dashboard
The calendar integration component can be used in the admin dashboard to:
1. Select a cleaner
2. Enter their Google Calendar credentials
3. Set up calendar integration
4. View their calendar events
5. Check availability

## Step 6: Testing the Integration

### 6.1 Test Calendar Authentication
1. Start the backend server: `python server.py`
2. Get the authorization URL: `GET http://localhost:8000/api/calendar/auth/url`
3. Open the returned URL in a browser
4. Complete the Google OAuth flow
5. Use the returned authorization code with the callback endpoint

### 6.2 Test Calendar Operations
1. Set up calendar integration for a cleaner using the admin endpoint
2. Retrieve calendar events to verify read access
3. Create a test booking to verify event creation
4. Check availability to ensure conflict detection works

## Step 7: Production Deployment

### 7.1 Update Redirect URIs
In Google Cloud Console, add your production domain:
- `https://yourdomain.com/api/calendar/auth/callback`

### 7.2 Environment Variables
Update your production environment variables:
```bash
GOOGLE_CLIENT_ID=your_production_client_id
GOOGLE_CLIENT_SECRET=your_production_client_secret
GOOGLE_REDIRECT_URI=https://yourdomain.com/api/calendar/auth/callback
```

### 7.3 Security Considerations
- Store credentials securely in your database
- Use HTTPS in production
- Implement proper error handling
- Monitor API usage and quotas

## Troubleshooting

### Common Issues

1. **"Invalid redirect URI" error**
   - Ensure the redirect URI in Google Console matches your environment variable
   - Check for trailing slashes and protocol (http vs https)

2. **"Access denied" error**
   - Verify the Google Calendar API is enabled
   - Check that the OAuth consent screen is configured
   - Ensure the user has granted the necessary permissions

3. **"Invalid credentials" error**
   - Verify the client ID and secret are correct
   - Check that the credentials haven't expired
   - Ensure the refresh token is included

4. **Calendar events not appearing**
   - Check the calendar ID (use 'primary' for the main calendar)
   - Verify the time range in the API call
   - Ensure the cleaner has events in their calendar

### Debug Steps
1. Check server logs for detailed error messages
2. Verify environment variables are loaded correctly
3. Test the Google Calendar API directly using the Google API Explorer
4. Use the Google Calendar service validation endpoint

## API Rate Limits

Google Calendar API has the following limits:
- 1,000,000 queries per day
- 100 queries per 100 seconds per user

Monitor your usage in the Google Cloud Console to avoid hitting these limits.

## Support

For additional help:
- Check the [Google Calendar API documentation](https://developers.google.com/calendar/api)
- Review the [Google OAuth 2.0 documentation](https://developers.google.com/identity/protocols/oauth2)
- Contact the development team for integration issues
