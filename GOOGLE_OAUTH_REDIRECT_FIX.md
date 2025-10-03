# Google OAuth Redirect URI Mismatch Fix

## Error: 400: redirect_uri_mismatch

This error occurs when the redirect URI in your Google OAuth configuration doesn't match what your application is sending.

## Current Configuration Analysis

### Backend Configuration
- **Redirect URI**: `http://localhost:8000/api/auth/google/callback`
- **Client ID**: From environment variable `GOOGLE_CLIENT_ID`

### Frontend Configuration  
- **Redirect URI**: `http://localhost:8000/api/auth/google/callback` (from Login.js)
- **Client ID**: `758684152649-bibv1smukqo58p8q8mk1nuud19edq68a.apps.googleusercontent.com`

## Fix Steps

### Step 1: Update Google Cloud Console

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Navigate to "APIs & Services" > "Credentials"

2. **Find Your OAuth 2.0 Client**
   - Look for client ID: `758684152649-bibv1smukqo58p8q8mk1nuud19edq68a.apps.googleusercontent.com`
   - Click the edit (pencil) icon

3. **Update Authorized Redirect URIs**
   Add these exact URIs (case-sensitive):
   ```
   http://localhost:8000/api/auth/google/callback
   http://localhost:3000/api/auth/google/callback
   https://yourdomain.com/api/auth/google/callback
   ```

4. **Update Authorized JavaScript Origins**
   Add these origins:
   ```
   http://localhost:3000
   http://localhost:8000
   https://yourdomain.com
   ```

### Step 2: Verify Environment Variables

#### Backend (.env file)
```bash
GOOGLE_CLIENT_ID=758684152649-bibv1smukqo58p8q8mk1nuud19edq68a.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback
```

#### Frontend (.env file)
```bash
REACT_APP_GOOGLE_CLIENT_ID=758684152649-bibv1smukqo58p8q8mk1nuud19edq68a.apps.googleusercontent.com
REACT_APP_BACKEND_URL=http://localhost:8000
```

### Step 3: Check OAuth Consent Screen

1. **Go to OAuth Consent Screen**
   - In Google Cloud Console, go to "APIs & Services" > "OAuth consent screen"

2. **Verify App Status**
   - Ensure your app is in "Testing" mode for development
   - Add your email as a test user if in testing mode

3. **Check Required Fields**
   - App name: "Maids of CyFair"
   - User support email: your email
   - Developer contact: your email

### Step 4: Test the Fix

1. **Clear Browser Data**
   ```bash
   # Clear cookies and local storage
   # Restart your browser
   ```

2. **Start Your Servers**
   ```bash
   # Backend
   cd backend
   python server.py
   
   # Frontend (in new terminal)
   cd frontend
   npm start
   ```

3. **Test OAuth Flow**
   - Go to http://localhost:3000
   - Click "Sign in with Google"
   - Should redirect to Google OAuth
   - Complete the flow
   - Should redirect back to your app

## Common Issues and Solutions

### Issue 1: Still Getting redirect_uri_mismatch
**Solution**: 
- Double-check the exact URI in Google Cloud Console
- Ensure no trailing slashes
- Check for typos in the URI

### Issue 2: OAuth Opens in Embedded Context
**Solution**: 
- The current code uses `window.open()` which should open in system browser
- If still embedded, check if you're in an iframe or embedded context

### Issue 3: App Not Verified Error
**Solution**:
- Keep your app in "Testing" mode for development
- Add test users to your OAuth consent screen
- Complete app verification only for production

### Issue 4: Different Client IDs
**Solution**:
- Ensure both frontend and backend use the same Google Client ID
- Check your environment variables are loaded correctly

## Verification Checklist

- [ ] Google Cloud Console has correct redirect URIs
- [ ] Environment variables are set correctly
- [ ] OAuth consent screen is configured
- [ ] Test users are added (if in testing mode)
- [ ] Browser cache is cleared
- [ ] Both servers are running
- [ ] OAuth flow opens in system browser

## Production Considerations

When deploying to production:

1. **Update Redirect URIs**
   ```
   https://yourdomain.com/api/auth/google/callback
   ```

2. **Update Environment Variables**
   ```bash
   GOOGLE_REDIRECT_URI=https://yourdomain.com/api/auth/google/callback
   REACT_APP_BACKEND_URL=https://yourdomain.com
   ```

3. **App Verification**
   - Complete Google's app verification process
   - Submit for review if needed

## Debug Information

If you're still having issues, check:

1. **Network Tab**: Look for the exact redirect URI being sent
2. **Console Logs**: Check for any JavaScript errors
3. **Backend Logs**: Check server logs for OAuth errors
4. **Google Cloud Console**: Verify the configuration matches

The key is ensuring the redirect URI in Google Cloud Console exactly matches what your application sends.
