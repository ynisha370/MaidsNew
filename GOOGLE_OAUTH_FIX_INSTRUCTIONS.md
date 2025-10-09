# Google OAuth Configuration Fix - Complete Instructions

## Overview
This guide will help you fix the `redirect_uri_mismatch` error and ensure Google Sign Up/Sign In works correctly.

---

## Part 1: Environment Files Configuration

### Backend Environment File (`backend/.env`)

Open `backend/.env` and ensure these variables are set correctly:

```bash
# Google OAuth Configuration
GOOGLE_CLIENT_ID=758684152649-bibv1smukqo58p8q8mk1nuud19edq68a.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_actual_google_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback
```

**Important Notes:**
- Replace `your_actual_google_client_secret_here` with your actual Google Client Secret from Google Cloud Console
- The redirect URI MUST be exactly `http://localhost:8000/api/auth/google/callback`
- Do not add trailing slashes or modify the URI

### Frontend Environment File (`frontend/.env`)

Open `frontend/.env` and ensure these variables are set correctly:

```bash
# Backend API URL
REACT_APP_BACKEND_URL=http://localhost:8000

# Google OAuth Configuration
REACT_APP_GOOGLE_CLIENT_ID=758684152649-bibv1smukqo58p8q8mk1nuud19edq68a.apps.googleusercontent.com

# Stripe Configuration
REACT_APP_STRIPE_PUBLISHABLE_KEY=pk_test_51RzKQdRps3Ulo01CKof4M3aPKgizeI6LEFLs3hvVPj0wBS5rqYqAD2VgmELzDSoFkBJ8MLuLIdNoySlBeBIYWJMt00lL0R0w67
```

---

## Part 2: Google Cloud Console Configuration

### Step 1: Access Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account (nitin23359@iiitd.ac.in)
3. Select the project "maidsofcyfair" (or the correct project name)

### Step 2: Navigate to OAuth Credentials

1. In the left sidebar, click on **"APIs & Services"**
2. Click on **"Credentials"**
3. Find your OAuth 2.0 Client ID:
   - Look for Client ID: `758684152649-bibv1smukqo58p8q8mk1nuud19edq68a.apps.googleusercontent.com`
   - It should be named something like "Web client" or similar
4. Click the **Edit (pencil icon)** button

### Step 3: Configure Authorized Redirect URIs

In the "Authorized redirect URIs" section, add these exact URIs (if not already present):

```
http://localhost:8000/api/auth/google/callback
http://localhost:3000
```

**Important:**
- URIs are case-sensitive
- No trailing slashes
- Must match exactly what the application sends
- You can add both development and production URIs

### Step 4: Configure Authorized JavaScript Origins

In the "Authorized JavaScript origins" section, add these origins:

```
http://localhost:3000
http://localhost:8000
```

### Step 5: Save Configuration

1. Click **"Save"** at the bottom of the page
2. Wait 5-10 minutes for changes to propagate (Google sometimes caches OAuth configurations)

### Step 6: Verify OAuth Consent Screen

1. Go back to "APIs & Services"
2. Click on **"OAuth consent screen"**
3. Verify:
   - App is in **"Testing"** mode (for development)
   - Your email (nitin23359@iiitd.ac.in) is added as a test user
   - All required fields are filled in
4. If the app is in "Testing" mode, add yourself as a test user:
   - Scroll down to "Test users"
   - Click "Add Users"
   - Add: nitin23359@iiitd.ac.in
   - Click "Save"

---

## Part 3: Verify Backend is Running

Before testing, ensure your backend server is running:

```bash
cd backend
python server.py
```

The server should start on `http://localhost:8000`

---

## Part 4: Verify Frontend is Running

Ensure your frontend is running:

```bash
cd frontend
npm start
```

The app should open at `http://localhost:3000`

---

## Part 5: Clear Cache and Test

### Before Testing:

1. **Clear Browser Cache:**
   - Open Chrome/Edge: Press `Ctrl+Shift+Delete` (Windows) or `Cmd+Shift+Delete` (Mac)
   - Select "All time"
   - Check "Cookies and other site data"
   - Check "Cached images and files"
   - Click "Clear data"

2. **Alternative: Use Incognito/Private Mode:**
   - Open a new Incognito/Private window
   - Go to `http://localhost:3000`

### Testing Google Sign Up:

1. Navigate to `http://localhost:3000/register`
2. Click "Sign up with Google" button
3. You should see a new tab/window open with Google sign-in
4. Select your Google account (nitin23359@iiitd.ac.in)
5. Grant permissions if asked
6. You should be redirected back to the app
7. Check that:
   - No error messages appear
   - You are logged in
   - Your name and email are displayed correctly

### Testing Google Sign In:

1. Log out (if logged in)
2. Navigate to `http://localhost:3000/login`
3. Click "Sign in with Google" button
4. Select your Google account
5. You should be automatically signed in
6. Verify you can access your dashboard

### Testing Cleaner Google Sign In:

1. Navigate to `http://localhost:3000/cleaner/login`
2. Click "Sign in with Google" button
3. Follow the same process
4. Verify cleaner role and permissions

---

## Part 6: Troubleshooting

### Error: "redirect_uri_mismatch"

**Solution:**
- Double-check the redirect URI in Google Cloud Console matches exactly: `http://localhost:8000/api/auth/google/callback`
- Wait 10 minutes after saving changes in Google Cloud Console
- Clear browser cache completely
- Try in incognito mode

### Error: "This app isn't verified"

**Solution:**
- This is normal for apps in Testing mode
- Click "Advanced" → "Go to [app name] (unsafe)"
- OR add your email as a test user in OAuth consent screen

### Error: "Access blocked: Authorization Error"

**Solution:**
- Verify your email is added as a test user in OAuth consent screen
- Ensure the app is in "Testing" mode
- Check that the OAuth consent screen is properly configured

### Error: "Invalid request"

**Solution:**
- Check that GOOGLE_CLIENT_ID matches in both frontend and backend .env files
- Verify the client ID in Google Cloud Console is correct
- Restart both frontend and backend servers after changing .env files

### User Not Created in Database

**Check:**
1. Backend logs for errors
2. MongoDB connection is working
3. Run this test script: `python test_google_oauth.py` (see Part 7)

---

## Part 7: Verification Checklist

Before marking this as complete, verify:

- [ ] Backend `.env` has correct GOOGLE_CLIENT_ID and GOOGLE_REDIRECT_URI
- [ ] Frontend `.env` has correct REACT_APP_GOOGLE_CLIENT_ID
- [ ] Google Cloud Console has correct redirect URIs configured
- [ ] Google Cloud Console has correct JavaScript origins configured
- [ ] Your email is added as a test user in OAuth consent screen
- [ ] Backend server is running on port 8000
- [ ] Frontend is running on port 3000
- [ ] Cache is cleared or using incognito mode
- [ ] Google Sign Up creates a new user successfully
- [ ] Google Sign In logs in existing user successfully
- [ ] User data is stored correctly in MongoDB
- [ ] No console errors in browser developer tools
- [ ] No errors in backend logs

---

## Part 8: Getting Your Google Client Secret

If you need to find or regenerate your Google Client Secret:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to "APIs & Services" → "Credentials"
3. Find your OAuth 2.0 Client ID
4. Click on the client ID name (not the edit button)
5. You'll see:
   - **Client ID**: 758684152649-bibv1smukqo58p8q8mk1nuud19edq68a.apps.googleusercontent.com
   - **Client Secret**: (click to reveal or copy)
6. Copy the Client Secret and add it to `backend/.env`

**Note:** Never commit your Client Secret to version control. It's already in .gitignore.

---

## Support

If you continue to encounter issues after following all steps:

1. Check browser console for specific error messages (F12 → Console)
2. Check backend logs for detailed error messages
3. Run the automated test script (next section)
4. Verify all environment variables are loaded correctly

---

## Quick Test Commands

```bash
# Test backend OAuth endpoint
curl http://localhost:8000/api/auth/google/callback

# Check if backend is running
curl http://localhost:8000/health

# View backend logs (if running)
tail -f backend/server.log
```

