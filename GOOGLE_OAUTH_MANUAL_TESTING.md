# Google OAuth Manual Testing Guide

## Prerequisites

Before starting the manual tests, ensure:

1. ✅ Backend server is running on http://localhost:8000
2. ✅ Frontend is running on http://localhost:3000
3. ✅ MongoDB is running and accessible
4. ✅ Google Cloud Console is configured correctly (see GOOGLE_OAUTH_FIX_INSTRUCTIONS.md)
5. ✅ Environment files are properly configured
6. ✅ Automated tests pass: `python test_google_oauth.py`

---

## Test 1: Google Sign Up (New User Registration)

### Objective
Verify that a new user can create an account using Google OAuth.

### Steps

1. **Open the application**
   - Navigate to http://localhost:3000/register
   - Open browser Developer Tools (F12)
   - Go to Console tab

2. **Click "Sign up with Google"**
   - A new tab/window should open
   - You should see the Google account selection screen

3. **Select your Google account**
   - Choose your account (nitin23359@iiitd.ac.in)
   - If prompted, grant permissions

4. **Verify successful registration**
   - Check that you're redirected back to http://localhost:3000
   - You should see a success message: "Account created successfully with Google!"
   - You should be automatically logged in
   - Check the navigation bar shows your name/email

5. **Verify in browser console**
   - Check Developer Tools Console for any errors
   - Look for: "Google OAuth success" message
   - Look for: "Successfully signed in with Google!" toast

6. **Verify in database**
   ```bash
   # Connect to MongoDB
   mongosh
   use maidsofcyfair
   db.users.find({ email: "nitin23359@iiitd.ac.in" }).pretty()
   ```
   
   Verify the user document has:
   - ✅ `email`: nitin23359@iiitd.ac.in
   - ✅ `first_name`: Your first name from Google
   - ✅ `last_name`: Your last name from Google
   - ✅ `google_id`: Your Google ID (string)
   - ✅ `role`: "customer"
   - ✅ `password_hash`: null (OAuth users don't have password)
   - ✅ `created_at`: Recent timestamp
   - ✅ `updated_at`: Recent timestamp

### Expected Results

✅ **Success Criteria:**
- New user is created in database
- User is automatically logged in
- Success toast appears
- No errors in console
- User can access dashboard/protected routes

❌ **Failure Indicators:**
- Redirect URI mismatch error
- User not created in database
- Console shows errors
- Not logged in after OAuth flow

---

## Test 2: Google Sign In (Existing User Login)

### Objective
Verify that an existing user (created via Google OAuth) can sign in again.

### Steps

1. **Log out**
   - Click the logout button
   - Verify you're logged out

2. **Navigate to login page**
   - Go to http://localhost:3000/login
   - Open Developer Tools (F12)

3. **Click "Sign in with Google"**
   - New tab/window opens with Google sign-in

4. **Select your account**
   - Choose the same account (nitin23359@iiitd.ac.in)
   - May not need to grant permissions again

5. **Verify successful login**
   - Redirected to http://localhost:3000
   - Success message: "Successfully signed in with Google!"
   - You're logged in with your existing account
   - Your previous data is still there

6. **Verify user not duplicated**
   ```bash
   mongosh
   use maidsofcyfair
   db.users.countDocuments({ email: "nitin23359@iiitd.ac.in" })
   # Should return 1, not 2
   ```

### Expected Results

✅ **Success Criteria:**
- Existing user is found and logged in
- No duplicate user created
- Success toast appears
- User data preserved
- No errors in console

❌ **Failure Indicators:**
- New user created instead of using existing
- Login fails
- Duplicate users in database

---

## Test 3: Google Sign In for Existing Email User (Password-based)

### Objective
Verify what happens when a user who registered with email/password tries to sign in with Google.

### Steps

1. **Create a user with email/password**
   - Register normally with email and password
   - Use a different email or create test user

2. **Log out**

3. **Try to sign in with Google using the same email**
   - Click "Sign in with Google"
   - Select the account with the same email

4. **Verify behavior**
   - User should be able to sign in
   - Google ID should be added to existing user record
   - No duplicate user created

### Expected Results

✅ **Success Criteria:**
- User logs in successfully
- Existing user record updated with `google_id`
- No duplicate created

---

## Test 4: Cleaner Google Sign In

### Objective
Verify that cleaners can also sign in with Google.

### Steps

1. **Navigate to cleaner login**
   - Go to http://localhost:3000/cleaner/login

2. **Click "Sign in with Google"**
   - New tab opens with Google sign-in

3. **Complete OAuth flow**
   - Select account
   - Grant permissions if needed

4. **Verify cleaner login**
   - Should redirect to cleaner dashboard
   - Verify role is "cleaner" (if signing in as cleaner)
   - OR verify role is "customer" (if new cleaner signing up)

### Expected Results

✅ **Success Criteria:**
- OAuth flow completes
- User logged in with appropriate role
- Cleaner-specific features accessible (if cleaner role)

---

## Test 5: Multiple Account Selection

### Objective
Verify behavior when user has multiple Google accounts.

### Steps

1. **Ensure you have multiple Google accounts**
   - Add another Google account to browser

2. **Try sign in**
   - Click "Sign in with Google"
   - Select different account each time

3. **Verify**
   - Different accounts create different users
   - Each account can sign in independently
   - Correct account is always logged in

### Expected Results

✅ **Success Criteria:**
- Can switch between different Google accounts
- Each account maps to correct user

---

## Test 6: OAuth Flow Cancellation

### Objective
Verify graceful handling when user cancels OAuth flow.

### Steps

1. **Click "Sign in with Google"**

2. **Close the Google sign-in window**
   - Don't select account, just close the window

3. **Verify behavior**
   - User stays on login page
   - No error messages appear (or graceful error)
   - Can try again

### Expected Results

✅ **Success Criteria:**
- No crashes or unhandled errors
- User can retry OAuth

---

## Test 7: Permissions Denial

### Objective
Verify handling when user denies permissions.

### Steps

1. **Click "Sign in with Google"**

2. **Select account but deny permissions**
   - Click "Cancel" or "Deny"

3. **Verify error handling**
   - User redirected back to app
   - Error message displayed
   - Can retry

### Expected Results

✅ **Success Criteria:**
- Error handled gracefully
- Clear message to user
- Can retry OAuth

---

## Test 8: Network Errors

### Objective
Verify handling of network issues during OAuth.

### Steps

1. **Start OAuth flow**

2. **Simulate network issue**
   - Turn off internet briefly
   - Or block backend server

3. **Verify error handling**
   - Appropriate error message
   - No app crash

### Expected Results

✅ **Success Criteria:**
- Network errors handled
- User informed of issue
- App remains functional

---

## Test 9: Token Exchange

### Objective
Verify backend correctly exchanges authorization code for access token.

### Steps

1. **Complete OAuth flow**

2. **Monitor backend logs**
   ```bash
   tail -f backend/server.log
   ```

3. **Look for log entries:**
   - "Google OAuth callback received code"
   - "Token exchange request"
   - "Token response status: 200"
   - "Existing user found" or "Creating new user"

### Expected Results

✅ **Success Criteria:**
- Code exchange successful
- Access token received
- User info retrieved from Google
- JWT token generated

---

## Test 10: Console Debugging

### Objective
Verify debugging information in browser console.

### Steps

1. **Open Developer Tools Console**

2. **Click "Sign in with Google"**

3. **Check console output:**
   - "Environment check" logs
   - "OAuth Debug Information" logs
   - Client ID displayed
   - Redirect URI displayed
   - Full OAuth URL logged

4. **Verify values match configuration**

### Expected Results

✅ **Success Criteria:**
- Debug logs present
- Values match .env files
- No console errors

---

## Troubleshooting Common Issues

### Issue: "redirect_uri_mismatch"

**Diagnosis:**
- Open browser console
- Find the "Redirect URI (raw)" log
- Copy the exact URI

**Solution:**
- Add this EXACT URI to Google Cloud Console
- Wait 10 minutes
- Clear cache and retry

### Issue: "Invalid request"

**Diagnosis:**
- Check client ID in console logs
- Verify it matches Google Cloud Console

**Solution:**
- Update .env files with correct client ID
- Restart backend and frontend
- Retry

### Issue: User not created in database

**Diagnosis:**
- Check backend logs for errors
- Verify MongoDB connection

**Solution:**
- Ensure MongoDB is running
- Check database connection string
- Verify user permissions

### Issue: "This app isn't verified"

**Solution:**
- Click "Advanced" → "Go to app (unsafe)"
- OR add your email as test user in OAuth consent screen
- This is normal for development

---

## Verification Checklist

After completing all tests, verify:

- [ ] ✅ New users can sign up with Google
- [ ] ✅ Existing users can sign in with Google
- [ ] ✅ Users are created in MongoDB correctly
- [ ] ✅ Google ID is stored properly
- [ ] ✅ No duplicate users created
- [ ] ✅ JWT tokens generated correctly
- [ ] ✅ Protected routes accessible after OAuth login
- [ ] ✅ User data displayed correctly in UI
- [ ] ✅ Cleaner Google login works
- [ ] ✅ No console errors
- [ ] ✅ Backend logs show successful OAuth flow
- [ ] ✅ Can log out and log back in
- [ ] ✅ Multiple Google accounts work independently

---

## Success Confirmation

When all tests pass, you should be able to:

1. ✅ Sign up with Google (new user)
2. ✅ Sign in with Google (existing user)
3. ✅ Access all protected routes
4. ✅ User data stored correctly in database
5. ✅ No errors in console or backend logs
6. ✅ OAuth flow completes in < 5 seconds

**Congratulations!** 🎉 Google OAuth is working correctly.

---

## Next Steps

After successful testing:

1. **Test on other browsers**
   - Chrome ✅
   - Firefox
   - Safari
   - Edge

2. **Test with different Google accounts**
   - Personal Gmail
   - Organization G Suite account
   - Multiple accounts

3. **Production deployment**
   - Update redirect URIs for production domain
   - Update environment variables
   - Verify OAuth consent screen for production
   - Complete app verification if needed

4. **Documentation**
   - Update user documentation
   - Add OAuth troubleshooting to FAQ
   - Document for other developers

