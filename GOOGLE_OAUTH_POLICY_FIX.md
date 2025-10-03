# Google OAuth 2.0 Policy Compliance Fix

## Issue
You're encountering the error: "You can't sign in to this app because it doesn't comply with Google's OAuth 2.0 policy for keeping apps secure"

## Root Causes Identified
1. **Redirect URI Mismatch**: Frontend and backend were using different redirect URIs
2. **Embedded WebView Usage**: OAuth was opening in embedded context instead of system browser
3. **Inconsistent OAuth Configuration**: Multiple OAuth flows with different configurations

## Fixes Applied

### 1. Standardized Redirect URIs
- **Before**: Mixed URIs (`/auth/google/callback` vs `/calendar/auth/callback`)
- **After**: Unified to `http://localhost:8000/api/auth/google/callback`

### 2. Updated OAuth Flow to Prevent WebView Issues
- **Before**: `window.location.href = googleAuthUrl` (could trigger in embedded context)
- **After**: `window.open(googleAuthUrl, '_blank', 'noopener,noreferrer')` (opens in system browser)

### 3. Enhanced OAuth Parameters
- Added `access_type=offline` for refresh tokens
- Added `prompt=consent` to ensure proper consent flow
- Standardized redirect URI usage across all components

## Google Cloud Console Configuration Required

### Step 1: Update OAuth 2.0 Client Configuration
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to "APIs & Services" > "Credentials"
3. Find your OAuth 2.0 Client ID
4. Click "Edit" (pencil icon)

### Step 2: Update Authorized Redirect URIs
Add these URIs to your OAuth client:
```
http://localhost:8000/api/auth/google/callback
https://yourdomain.com/api/auth/google/callback
```

### Step 3: Verify OAuth Consent Screen
1. Go to "OAuth consent screen"
2. Ensure your app is in "Testing" mode or "Production" mode
3. Add test users if in testing mode
4. Verify all required fields are filled

### Step 4: Check App Verification Status
- If your app requires verification, complete the verification process
- For development, ensure you're in "Testing" mode with test users added

## Environment Variables Update

### Backend (.env)
```bash
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback
```

### Frontend (.env)
```bash
REACT_APP_GOOGLE_CLIENT_ID=your_google_client_id_here
REACT_APP_BACKEND_URL=http://localhost:8000
```

## Testing the Fix

### 1. Clear Browser Data
- Clear cookies and local storage
- Restart your browser

### 2. Test OAuth Flow
1. Start your backend server: `cd backend && python server.py`
2. Start your frontend: `cd frontend && npm start`
3. Try Google Sign-in - it should now open in a new tab
4. Complete the OAuth flow

### 3. Verify No WebView Issues
- OAuth should open in system browser, not embedded context
- No "doesn't comply with Google's OAuth 2.0 policy" error

## Additional Security Measures

### 1. HTTPS in Production
- Use HTTPS redirect URIs in production
- Update `GOOGLE_REDIRECT_URI` to use HTTPS

### 2. Domain Verification
- Verify your domain in Google Cloud Console
- Add your production domain to authorized origins

### 3. Scope Management
- Only request necessary scopes
- Current scopes: `openid email profile`

## Troubleshooting

### If Still Getting Policy Error:
1. **Check Browser**: Try in incognito/private mode
2. **Clear Cache**: Clear all browser data
3. **Verify URIs**: Ensure exact match in Google Cloud Console
4. **Check App Status**: Verify app is not in restricted state

### Common Issues:
- **Redirect URI mismatch**: Must be exact match
- **App not verified**: Complete verification process
- **Embedded context**: Ensure OAuth opens in system browser
- **Deprecated methods**: Use current OAuth 2.0 flow

## Code Changes Made

### Frontend Changes:
- `Login.js`: Updated OAuth flow to use system browser
- `Register.js`: Updated OAuth flow to use system browser  
- `GoogleCallback.js`: Updated to use consistent backend URL

### Backend Changes:
- `env_template`: Standardized redirect URI
- OAuth callback endpoint already properly configured

## Next Steps
1. Update your Google Cloud Console with the new redirect URIs
2. Test the OAuth flow
3. Deploy to production with HTTPS redirect URIs
4. Complete app verification if required

This fix addresses the core Google OAuth 2.0 policy compliance issues and should resolve the authentication error.
