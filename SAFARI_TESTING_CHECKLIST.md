# Safari Testing Checklist ✅

## Test These Features in Safari

### 1. Login Functionality
- [ ] Navigate to https://foodsensescale.tech
- [ ] Click "Login" 
- [ ] Enter email and password
- [ ] Click "Sign In"
- [ ] **Expected:** Should successfully login and redirect to dashboard
- [ ] **Check console:** No CORS errors

### 2. Guest Checkout - Calendar
- [ ] Navigate to https://foodsensescale.tech/guest-booking
- [ ] Select house size and frequency
- [ ] Click "Next" to calendar selection
- [ ] **Expected:** Calendar should load with available dates
- [ ] **Check console:** No CORS errors on `/api/available-dates` call

### 3. Guest Checkout - Add-ons
- [ ] Continue from calendar step
- [ ] **Expected:** Add-on services should load and display
- [ ] Try adding/removing add-ons
- [ ] **Check console:** No CORS errors on `/api/services` call

### 4. Guest Checkout - Complete Booking
- [ ] Fill in all required information
- [ ] Submit booking
- [ ] **Expected:** Should process successfully
- [ ] **Check console:** No CORS errors on `/api/bookings` call

### 5. Google Sign-In (if applicable)
- [ ] Click "Sign in with Google"
- [ ] Complete Google OAuth flow
- [ ] **Expected:** Should redirect back and authenticate
- [ ] Note: May have separate OAuth config issues

---

## How to Check for CORS Errors in Safari

1. Open Safari
2. Go to Safari → Preferences → Advanced
3. Check "Show Develop menu in menu bar"
4. Navigate to your site
5. Press Cmd+Option+C to open Console
6. Look for errors containing:
   - "CORS"
   - "Access-Control-Allow-Origin"
   - "credentials mode"

---

## Expected Console Output in Safari

### ✅ GOOD (Should See):
```
Safari detected - Enhanced CORS configuration enabled
axios.defaults.withCredentials: true
BookingFlow - BACKEND_URL: https://foodsensescale.tech
Available dates loaded successfully
```

### ❌ BAD (Should NOT See):
```
CORS policy: No 'Access-Control-Allow-Origin' header
CORS policy: The value of the 'Access-Control-Allow-Origin' header must not be the wildcard '*'
credentials mode is 'include' but the 'Access-Control-Allow-Credentials' header is false
```

---

## Network Tab Verification

1. Open Safari Developer Tools (Cmd+Option+C)
2. Go to Network tab
3. Reload the page
4. Click on any API request (e.g., `/api/services`)
5. Check Response Headers:

### ✅ Should See:
```
access-control-allow-origin: https://foodsensescale.tech
access-control-allow-credentials: true
access-control-allow-methods: GET, POST, PUT, DELETE, OPTIONS, PATCH
```

### ❌ Should NOT See:
```
access-control-allow-origin: *
(with credentials: true at the same time)
```

---

## If Issues Persist

### 1. Clear Safari Cache
- Safari → Preferences → Privacy → Manage Website Data
- Search "foodsensescale.tech"
- Remove all data
- Restart Safari

### 2. Check Backend Logs
```bash
pm2 logs server --lines 50
```

### 3. Check Nginx Logs
```bash
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log
```

### 4. Verify Environment Variables
```bash
cat /root/MaidsNew/frontend/.env
```
Should show:
```
REACT_APP_BACKEND_URL=https://foodsensescale.tech
```

### 5. Test CORS Manually
```bash
# Test with correct origin
curl -I -H "Origin: https://foodsensescale.tech" https://foodsensescale.tech/api/services

# Should return:
# access-control-allow-origin: https://foodsensescale.tech
# access-control-allow-credentials: true
```

---

## Technical Details

### What Was Fixed:
1. ✅ Nginx CORS: Changed from wildcard `*` to specific origin `$http_origin`
2. ✅ Backend CORS: Changed from `allow_origins=["*"]` to specific domains
3. ✅ axios config: Added `withCredentials: true` globally
4. ✅ fetch() calls: Added `credentials: 'include'` to all fetch requests
5. ✅ Environment: Created `.env` with correct production URL
6. ✅ Frontend rebuild: Built with new environment variables
7. ✅ Services restarted: nginx reloaded, backend restarted via pm2

### Files Changed:
- `/etc/nginx/sites-available/foodsensescale.tech`
- `/root/MaidsNew/backend/server.py`
- `/root/MaidsNew/frontend/src/index.js`
- `/root/MaidsNew/frontend/src/components/GoogleCallback.js`
- `/root/MaidsNew/frontend/.env` (created)

---

## Success Criteria

✅ **Safari Compatibility Achieved When:**
1. No CORS errors in Safari console
2. Login works successfully
3. Guest checkout calendar loads
4. Guest checkout add-ons load
5. All API calls complete successfully
6. No "credentials mode" errors
7. No "wildcard origin" errors

---

## Support

If you still see issues after trying all the above:
1. Share Safari console logs
2. Share Network tab screenshots showing headers
3. Share any error messages
4. Verify you're testing on https://foodsensescale.tech (not HTTP or localhost)

**For more details, see:** `SAFARI_COMPATIBILITY_FIX.md`

