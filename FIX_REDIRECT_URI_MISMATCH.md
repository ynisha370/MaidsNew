# Fix redirect_uri_mismatch Error - Step by Step

**Error:** `{"detail":"Authentication failed: 400: Token exchange failed: redirect_uri_mismatch"}`

**Cause:** Google Cloud Console doesn't have the correct redirect URI configured.

---

## ✅ SOLUTION - Add This Exact URI to Google Cloud Console:

```
https://foodsensescale.tech/api/auth/google/callback
```

---

## 📋 Step-by-Step Instructions:

### 1. In Google Cloud Console (the screen you showed me):

Scroll to the **"Authorized redirect URIs"** section

### 2. Click the **"+ Add URI"** button

### 3. Type or paste this EXACT URL:
```
https://foodsensescale.tech/api/auth/google/callback
```
**IMPORTANT:** Must include `/api/auth/google/` - this is the critical part!

### 4. Your redirect URIs should look like this:
```
URIs 1: http://localhost:8000/api/auth/google/callback
URIs 2: https://foodsensescale.tech/api/auth/google/callback  ← NEW ONE TO ADD
```

### 5. REMOVE these incorrect URIs (optional but recommended):
- `http://localhost:3000` (not a redirect URI)
- `https://foodsensescale.tech/login` (wrong path)
- `https://foodsensescale.tech/callback` (missing /api/auth/google/)
- `https://foodsensescale.tech/auth/google/callback` (missing /api/)

### 6. Click **"Save"** button at the bottom

### 7. Wait 5-10 minutes for Google to propagate changes

### 8. Clear browser cache or use Incognito mode

### 9. Test again - Go to https://foodsensescale.tech/login and click "Sign in with Google"

---

## 🎯 What's Currently Wrong:

**Backend expects:** `https://foodsensescale.tech/api/auth/google/callback`

**Google Console has:**
- ❌ `https://foodsensescale.tech/callback`
- ❌ `https://foodsensescale.tech/auth/google/callback`

**Neither matches exactly!** The `/api/` part is crucial.

---

## ✅ After Fix:

Once you add the correct URI and wait 5-10 minutes:
- Google OAuth will work correctly
- Users can sign in with Google
- No more redirect_uri_mismatch errors

---

## 💡 Remember:

- URIs must match **EXACTLY** (case-sensitive, including all slashes)
- Changes can take up to 10 minutes to propagate
- Clear browser cache after making changes
- Test in Incognito mode if cache clearing doesn't work

