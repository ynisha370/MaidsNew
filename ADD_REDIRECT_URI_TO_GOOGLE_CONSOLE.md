# 🚨 URGENT: Add Redirect URI to Google Cloud Console

## ✅ Good News
The app is now correctly configured and sending the right redirect URI:
```
https://foodsensescale.tech/api/auth/google/callback
```

## ❌ The Problem
This redirect URI is **NOT registered** in your Google Cloud Console for client ID:
```
758684152649-uss73uc32io23s8l519lc2fcem4u6adc.apps.googleusercontent.com
```

---

## 🔧 IMMEDIATE ACTION REQUIRED

### Step 1: Go to Google Cloud Console
Visit: https://console.cloud.google.com/apis/credentials

### Step 2: Find Your OAuth Client
Look for the OAuth 2.0 Client ID that starts with:
```
758684152649-uss73uc32io23s8l519lc2fcem4u6adc
```

Click on it to edit.

### Step 3: Add the Redirect URI

In the **"Authorized redirect URIs"** section, you need to have these TWO URIs:

**REQUIRED URIs:**
```
https://foodsensescale.tech/api/auth/google/callback
http://localhost:8000/api/auth/google/callback
```

### Step 4: Remove Any Incorrect URIs

Based on your earlier screenshot, you had these WRONG URIs - **DELETE THEM:**
- ❌ `http://localhost:3000`
- ❌ `https://foodsensescale.tech/login`
- ❌ `https://foodsensescale.tech/callback`
- ❌ `https://foodsensescale.tech/auth/google/callback`

Keep ONLY:
- ✅ `https://foodsensescale.tech/api/auth/google/callback`
- ✅ `http://localhost:8000/api/auth/google/callback` (for local dev)

### Step 5: Update Authorized JavaScript Origins

In the **"Authorized JavaScript origins"** section, you should have:
```
https://foodsensescale.tech
http://localhost:3000
http://localhost:8000
```

### Step 6: Save and Wait
1. Click the **"Save"** button at the bottom
2. Wait **10-15 minutes** for Google to propagate the changes
3. Clear your browser cache or use Incognito mode

---

## 📸 Visual Guide

When you open your OAuth client in Google Cloud Console, you should see:

```
Authorized redirect URIs:
  URIs 1: https://foodsensescale.tech/api/auth/google/callback    ← ADD THIS
  URIs 2: http://localhost:8000/api/auth/google/callback

Authorized JavaScript origins:
  URIs 1: https://foodsensescale.tech
  URIs 2: http://localhost:3000
  URIs 3: http://localhost:8000
```

---

## ✅ Why This Will Fix It

Google is rejecting your OAuth request because:
1. ✅ Your app is sending: `https://foodsensescale.tech/api/auth/google/callback`
2. ❌ Google Cloud Console doesn't have this URI registered
3. 🔒 Google blocks unregistered redirect URIs for security

Once you add it to Google Cloud Console, it will work!

---

## ⏰ Timeline

- **Add URI to Google Console:** 2 minutes
- **Google propagation time:** 10-15 minutes
- **Clear browser cache:** 1 minute
- **Test OAuth:** 1 minute

Total: ~15-20 minutes until it works

---

## 🎯 Exact URI to Add

Copy this EXACTLY (no spaces, no typos):
```
https://foodsensescale.tech/api/auth/google/callback
```

Paste it in the "Authorized redirect URIs" section and click Save.

---

## 🔍 After Saving

To verify it worked:
1. Wait 10-15 minutes
2. Open Incognito/Private browser window
3. Go to: https://foodsensescale.tech/login
4. Click "Sign in with Google"
5. Should work without policy error! ✅

---

## ❓ If You Can't Find the OAuth Client

1. Go to: https://console.cloud.google.com/
2. Select your project
3. Click "APIs & Services" in left menu
4. Click "Credentials"
5. Look for "OAuth 2.0 Client IDs" section
6. Find the one with ID: `758684152649-uss73uc32io23s8l519lc2fcem4u6adc...`

---

**Your app is correctly configured. You just need to register the redirect URI in Google Cloud Console!**

