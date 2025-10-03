# Debug OAuth Redirect URI Mismatch

## Step 1: Check What Redirect URI is Being Sent

1. **Open your browser's Developer Tools**
   - Press F12 or right-click → Inspect
   - Go to the Console tab

2. **Try Google Sign-in**
   - Click "Sign in with Google"
   - Look at the console output for debug information

3. **Copy the exact redirect URI from the console**
   - Look for: "Redirect URI (raw): http://localhost:8000/api/auth/google/callback"
   - This is the EXACT URI you need to add to Google Cloud Console

## Step 2: Google Cloud Console Configuration

### 2.1 Go to Google Cloud Console
- Visit: https://console.cloud.google.com/
- Navigate to "APIs & Services" > "Credentials"

### 2.2 Find Your OAuth 2.0 Client
- Look for client ID: `758684152649-bibv1smukqo58p8q8mk1nuud19edq68a.apps.googleusercontent.com`
- Click the edit (pencil) icon

### 2.3 Add Authorized Redirect URIs
Add these EXACT URIs (copy from console output):
```
http://localhost:8000/api/auth/google/callback
http://localhost:3000/api/auth/google/callback
```

### 2.4 Add Authorized JavaScript Origins
```
http://localhost:3000
http://localhost:8000
```

### 2.5 Save Configuration
- Click "Save" at the bottom

## Step 3: Common Issues and Solutions

### Issue 1: Multiple OAuth Clients
If you have multiple OAuth clients, make sure you're editing the correct one:
- Check the client ID matches: `758684152649-bibv1smukqo58p8q8mk1nuud19edq68a.apps.googleusercontent.com`

### Issue 2: Wrong Project
Make sure you're in the correct Google Cloud project:
- Check the project name in the top bar
- Switch projects if needed

### Issue 3: Cached Configuration
Google sometimes caches OAuth configurations:
- Wait 5-10 minutes after saving
- Clear browser cache completely
- Try in incognito/private mode

### Issue 4: HTTPS vs HTTP
Make sure you're using the correct protocol:
- Development: `http://localhost:8000`
- Production: `https://yourdomain.com`

## Step 4: Verify Backend Endpoint

Check if your backend endpoint is working:

1. **Test the endpoint directly:**
   ```bash
   curl http://localhost:8000/api/auth/google/callback
   ```

2. **Check backend logs:**
   - Look for any errors when the OAuth callback is hit
   - Make sure the endpoint is properly configured

## Step 5: Alternative Solutions

### Option 1: Use Different Redirect URI
If the issue persists, try using the frontend URL as redirect:

1. **Update Login.js:**
   ```javascript
   const redirectUri = encodeURIComponent(`${window.location.origin}/auth/google/callback`);
   ```

2. **Add frontend route for OAuth callback**
3. **Update Google Cloud Console with frontend URL**

### Option 2: Check Environment Variables
Make sure your environment variables are correct:

1. **Frontend .env:**
   ```bash
   REACT_APP_GOOGLE_CLIENT_ID=758684152649-bibv1smukqo58p8q8mk1nuud19edq68a.apps.googleusercontent.com
   REACT_APP_BACKEND_URL=http://localhost:8000
   ```

2. **Backend .env:**
   ```bash
   GOOGLE_CLIENT_ID=758684152649-bibv1smukqo58p8q8mk1nuud19edq68a.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your_google_client_secret_here
   GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback
   ```

## Step 6: Debug Checklist

- [ ] Console shows the exact redirect URI being sent
- [ ] Google Cloud Console has the EXACT same URI
- [ ] No typos in the URI (case-sensitive)
- [ ] Correct protocol (http vs https)
- [ ] No trailing slashes
- [ ] Backend endpoint is accessible
- [ ] Environment variables are loaded correctly
- [ ] Browser cache is cleared
- [ ] Tried in incognito mode

## Step 7: Test the Fix

1. **Clear browser cache completely**
2. **Restart both servers:**
   ```bash
   # Backend
   cd backend && python server.py
   
   # Frontend (new terminal)
   cd frontend && npm start
   ```
3. **Try Google Sign-in**
4. **Check console for debug information**
5. **Should redirect successfully**

## If Still Not Working

1. **Check the exact error message**
2. **Copy the redirect URI from console**
3. **Verify it matches exactly in Google Cloud Console**
4. **Try creating a new OAuth client if needed**
5. **Check if there are any firewall or network issues**
