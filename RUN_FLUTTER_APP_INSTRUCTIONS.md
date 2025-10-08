# Running the Flutter Cleaner App on Android Studio Emulator

## ✅ Backend Status
Your backend server is running on: `http://0.0.0.0:8000`

## 📱 Steps to Run Flutter App on Android Emulator

### Step 1: Update API Configuration

The backend is running on port **8000** (not 5000), so we need to update the Flutter app configuration:

**File to edit**: `flutter_app/lib/config/api_config.dart`

Change the `baseUrl` to:
```dart
static const String baseUrl = 'http://10.0.2.2:8000';
```

> **Note**: `10.0.2.2` is the special IP that Android emulator uses to access the host machine's localhost.

---

### Step 2: Install Flutter (If Not Already Installed)

#### Windows:
1. Download Flutter SDK: https://docs.flutter.dev/get-started/install/windows
2. Extract to `C:\src\flutter`
3. Add to PATH: `C:\src\flutter\bin`
4. Restart PowerShell/CMD

#### Verify Installation:
```powershell
flutter --version
flutter doctor
```

#### Accept Android Licenses:
```powershell
flutter doctor --android-licenses
```

---

### Step 3: Open Android Studio

1. Open Android Studio
2. Go to: **Tools → Device Manager** (or **AVD Manager**)
3. Create a new Virtual Device if you don't have one:
   - Click **Create Device**
   - Select **Pixel 5** or any phone
   - Download system image (API 33 - Android 13 recommended)
   - Click **Finish**
4. Click the **Play ▶️** button to start the emulator
5. Wait for the emulator to fully boot (you'll see the home screen)

---

### Step 4: Navigate to Flutter App Directory

```powershell
cd flutter_app
```

---

### Step 5: Install Dependencies

```powershell
flutter pub get
```

This will download all required packages specified in `pubspec.yaml`.

---

### Step 6: Verify Device Connection

```powershell
flutter devices
```

You should see output like:
```
emulator-5554 • sdk gphone64 arm64 • android • Android 13 (API 33) (emulator)
```

---

### Step 7: Run the App

```powershell
flutter run
```

Or to run on a specific device:
```powershell
flutter run -d emulator-5554
```

---

## 🎯 Quick Commands (Copy-Paste)

### Option 1: Automated Script
```powershell
# From project root
cd flutter_app
flutter pub get
flutter devices
flutter run
```

### Option 2: Using the Batch File
```cmd
# Double-click or run:
flutter_app\run_android.bat
```

---

## 🔧 Troubleshooting

### Issue: "Flutter not found"
**Solution**: Add Flutter to PATH
```powershell
$env:Path += ";C:\src\flutter\bin"
```

### Issue: "No devices found"
**Solution**: 
1. Make sure Android emulator is running
2. Run: `flutter devices`
3. If still not detected, restart emulator

### Issue: "Android licenses not accepted"
**Solution**:
```powershell
flutter doctor --android-licenses
# Press 'y' for all
```

### Issue: "Gradle build failed"
**Solution**:
```powershell
cd flutter_app
flutter clean
flutter pub get
flutter run
```

### Issue: "Connection refused to backend"
**Solution**:
- Make sure backend is running: `http://localhost:8000`
- Verify API URL in `flutter_app/lib/config/api_config.dart` is `http://10.0.2.2:8000`

---

## 📝 Testing the App

### Default Login Credentials:

**Cleaner Account** (for testing the cleaner app):
- Email: `cleaner@maids.com`
- Password: `cleaner123`

**Demo Mode** (works without backend):
- Email: `demo@example.com`
- Password: `demo123`

---

## 🎨 What You'll See

Once the app launches:

1. **Splash Screen** → Shows "Cleaner App" logo
2. **Login Screen** → Enter cleaner credentials
3. **Dashboard** → Shows:
   - Welcome card with cleaner name and rating
   - Today's jobs count
   - Completed jobs count
   - Current balance
   - Total earnings
   - List of today's assigned jobs
4. **Navigation Tabs**:
   - 🏠 **Home** - Dashboard overview
   - 💼 **Jobs** - View all jobs (Today/Upcoming/Completed)
   - 💰 **Wallet** - View earnings and balance
   - 👤 **Profile** - View profile and settings

---

## 🚀 Hot Reload

While the app is running:
- Press `r` in terminal → Hot reload (fast, maintains state)
- Press `R` in terminal → Hot restart (full restart)
- Press `q` → Quit app

---

## 📱 App Features Available

✅ **Multi-user Login** - Multiple cleaners can login
✅ **Job Viewing** - See all assigned jobs
✅ **Clock In/Out** - Track work hours with GPS
✅ **Task Management** - Check off completed tasks
✅ **ETA Updates** - Send arrival time to clients
✅ **Client Messaging** - Communicate with customers
✅ **Earnings Dashboard** - View total earnings
✅ **Digital Wallet** - Check balance
✅ **Payment History** - See all transactions
✅ **Profile Management** - View stats and settings

---

## 🔄 Complete Testing Flow

1. **Login** as cleaner
2. **View Dashboard** - See today's jobs
3. **Go to Jobs Tab** - View all assigned jobs
4. **Click on a Job** - See job details
5. **Clock In** - Start working (GPS required)
6. **Update ETA** - "15 minutes away"
7. **Send Message** - "On my way!"
8. **Check Tasks** - Mark tasks as complete
9. **Clock Out** - Finish job
10. **View Wallet** - See updated earnings
11. **Check Payment History** - See transaction

---

## 📊 Expected Behavior

### First Run:
- App compiles (takes 2-5 minutes first time)
- Gradle downloads dependencies
- APK is installed on emulator
- App launches automatically

### Subsequent Runs:
- Much faster (30-60 seconds)
- Hot reload available during development
- Changes reflect instantly

---

## 🎯 Success Indicators

✅ Emulator is running
✅ `flutter devices` shows emulator
✅ `flutter run` compiles successfully
✅ App launches on emulator
✅ Login screen appears
✅ Can login with cleaner credentials
✅ Dashboard shows data
✅ Navigation works
✅ Can interact with jobs

---

## 📸 What to Expect

### Login Screen:
- Blue gradient background
- Email and password fields
- "Sign In" button
- "Sign Up" link

### Dashboard:
- Top: Welcome card with name and rating
- Stats cards showing jobs and earnings
- List of today's jobs
- Bottom navigation bar

### Jobs Screen:
- Three tabs: Today, Upcoming, Completed
- Job cards with client info, time, price
- Tap to see job details

### Job Detail:
- Client information
- Schedule and address
- Task checklist
- Clock in/out buttons
- ETA and messaging options

---

## 🆘 Need Help?

1. **Flutter Issues**: Run `flutter doctor -v`
2. **Emulator Issues**: Restart emulator
3. **Build Issues**: Run `flutter clean && flutter pub get`
4. **Backend Issues**: Check backend is on port 8000
5. **API Issues**: Verify `api_config.dart` has correct URL

---

## 🎉 Ready to Go!

Your cleaner app is ready to run. Just follow these steps:

```powershell
# 1. Make sure backend is running (it already is! ✅)
# 2. Start Android emulator
# 3. Run these commands:

cd flutter_app
flutter pub get
flutter run
```

The app will compile and launch on the emulator automatically! 🚀

---

**Need the API URL changed?** 
Edit: `flutter_app/lib/config/api_config.dart`
Change: `baseUrl = 'http://10.0.2.2:8000'`

