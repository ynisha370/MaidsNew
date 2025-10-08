# 🔐 App Login Guide - All Credentials

## 🎮 **Demo Mode** (Works Without Backend)

### Demo Credentials:
- **Email**: `demo@example.com`
- **Password**: `demo123`

**Features:**
- ✅ Login works immediately
- ✅ Dashboard shows demo stats
- ✅ Wallet shows demo balance ($345)
- ✅ Jobs list (empty but functional)
- ✅ All UI features working
- ✅ No backend required!

**Use this to test the app UI and navigation!**

---

## 🔧 **Real Backend Mode** (Requires Backend Running)

### Cleaner Account:
- **Email**: `cleaner@maids.com`
- **Password**: `cleaner123`

**Features:**
- ✅ Real data from backend
- ✅ Actual assigned jobs
- ✅ Real earnings
- ✅ Clock in/out works
- ✅ Messaging works
- ✅ Full backend integration

**Backend must be running on port 8000!**

---

## 🎯 **How to Switch Modes**

### Using Demo Mode (No Backend):
1. Open app on emulator
2. Login screen appears
3. Enter: `demo@example.com` / `demo123`
4. Click "Sign In"
5. Dashboard loads with demo data

### Using Real Backend:
1. Make sure backend is running: `http://localhost:8000`
2. Login with: `cleaner@maids.com` / `cleaner123`
3. App connects to backend
4. Real data loads

---

## 🐛 **If Login Fails:**

### Demo Mode Not Working:
The app has been updated with demo mode. Press `r` in terminal for hot reload, or restart the app.

### Backend Mode Not Working:
Check these:
1. Backend running? (Check terminal for "Uvicorn running on http://0.0.0.0:8000")
2. API URL correct? (Should be `http://10.0.2.2:8000` in `lib/config/api_config.dart`)
3. Cleaner user exists in database?

---

## ✅ **What's Available in Demo Mode:**

### Dashboard:
- Welcome card with "Demo Cleaner"
- Rating: 4.8 ⭐
- Completed Jobs: 127
- Balance: $345.00
- Total Earnings: $12,750.00

### Jobs Tab:
- Empty initially (no jobs assigned)
- UI is fully functional
- Can navigate between tabs

### Wallet Tab:
- Balance: $345.00
- Total Earnings: $12,750.00
- Withdrawals: $12,405.00
- Recent transactions: Empty

### Profile Tab:
- View demo cleaner profile
- Settings options
- Logout works

---

## 🔄 **Testing Flow**

### Demo Mode Testing:
```
1. Login → demo@example.com / demo123
2. View Dashboard → See demo stats
3. Jobs Tab → Browse empty list (UI works)
4. Wallet Tab → See demo balance
5. Profile → View profile, test logout
6. Login again → Test works repeatedly
```

### Backend Mode Testing:
```
1. Ensure backend running
2. Login → cleaner@maids.com / cleaner123
3. Dashboard → See real data
4. Jobs → View assigned jobs (if any)
5. Click job → Clock in/out
6. Wallet → See real earnings
```

---

## 🎨 **Current App Status on Emulator**

The app is currently **RUNNING** on your emulator!

### What You Should See:
- Login screen with blue gradient
- Email and password fields
- "Welcome Back" title
- "Sign in to continue" subtitle

### Try Now:
1. **Demo Login**: `demo@example.com` / `demo123`
2. **Real Login**: `cleaner@maids.com` / `cleaner123` (if backend running)

---

## 📱 **Hot Reload Commands**

While app is running in terminal:
- Press `r` → Hot reload (fast, after code changes)
- Press `R` → Hot restart (full restart)
- Press `q` → Quit app
- Press `h` → Help

---

## ✨ **Demo Mode Benefits**

✅ **No backend needed** - Test UI immediately  
✅ **No network errors** - Always works  
✅ **Instant login** - No waiting  
✅ **Pre-filled data** - See how it looks with data  
✅ **Perfect for testing** - Try all screens  

---

## 🎯 **Recommended Testing Order**

1. **Start with Demo Mode** (`demo@example.com`)
   - Test all UI features
   - Navigate all screens
   - Check all tabs work

2. **Then Try Backend Mode** (`cleaner@maids.com`)
   - See real data integration
   - Test clock in/out
   - Test messaging
   - Test real earnings

---

## 🎊 **Your App is Running!**

**Look at your Android emulator - the login screen should be visible!**

Try logging in with:
- `demo@example.com` / `demo123` ← **Works immediately!**

---

**Need help?** The app is running - just login and explore! 🚀

