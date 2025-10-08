# 🚀 How to Run the Flutter Cleaner App on Android

## ⚡ Quick Start (5 Steps)

### Step 1: Install Flutter (First Time Only)

#### Windows:
1. Download Flutter SDK: https://docs.flutter.dev/get-started/install/windows/mobile
2. Extract to `C:\src\flutter`
3. Add to System PATH:
   - Search "Environment Variables" in Windows
   - Edit "Path" variable
   - Add: `C:\src\flutter\bin`
   - Click OK
4. Open NEW command prompt and verify:
   ```cmd
   flutter --version
   ```

#### macOS:
```bash
# Install via Homebrew (recommended)
brew install flutter

# Or download manually from:
# https://docs.flutter.dev/get-started/install/macos/mobile-android
```

#### Linux:
```bash
# Download Flutter
cd ~
wget https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_3.16.0-stable.tar.xz
tar xf flutter_linux_3.16.0-stable.tar.xz

# Add to PATH (add to ~/.bashrc or ~/.zshrc)
export PATH="$PATH:$HOME/flutter/bin"

# Reload shell
source ~/.bashrc
```

---

### Step 2: Install Android Studio

1. Download: https://developer.android.com/studio
2. Install Android Studio
3. During installation, ensure these are selected:
   - Android SDK
   - Android SDK Platform
   - Android Virtual Device
4. Open Android Studio
5. Go to: More Actions → SDK Manager
6. Install:
   - Android SDK Platform (latest)
   - Android SDK Build-Tools
   - Android Emulator

---

### Step 3: Accept Android Licenses

Open terminal/command prompt:
```bash
flutter doctor --android-licenses
```
Type `y` to accept all licenses.

---

### Step 4: Create Android Emulator

1. Open Android Studio
2. Click: More Actions → Virtual Device Manager (or Tools → Device Manager)
3. Click: Create Device
4. Select: Pixel 5 (or any phone)
5. Click: Next
6. Download a system image (e.g., API 33 - Android 13)
7. Click: Next → Finish
8. Click ▶️ to start the emulator

---

### Step 5: Run the App

```bash
cd flutter_app
flutter pub get
flutter run
```

**Done!** 🎉 The app will launch on your emulator!

---

## 📱 Alternative: Run on Physical Android Device

### Enable Developer Mode:
1. Go to Settings → About Phone
2. Tap "Build Number" 7 times
3. Go back → Developer Options
4. Enable "USB Debugging"
5. Connect phone via USB
6. Accept debugging prompt on phone

### Run:
```bash
cd flutter_app
flutter devices  # Verify device is connected
flutter run
```

---

## 🎮 Using Demo Mode (No Backend Required)

The app includes built-in demo data for testing!

### Option 1: Login with Demo Credentials
1. Run the app
2. Use these credentials:
   - Email: `demo@example.com`
   - Password: `demo123`

### Option 2: Enable Full Demo Mode
Edit `lib/providers/auth_provider.dart` and add at the start of `login()` method:

```dart
Future<bool> login(String email, String password) async {
  // DEMO MODE - Remove for production
  if (email == 'demo@example.com' && password == 'demo123') {
    _currentUser = DemoData.getDemoCleaner();
    await _storageService.saveUser(_currentUser!);
    _isLoading = false;
    notifyListeners();
    return true;
  }
  // ... rest of the code
}
```

Then also update `job_provider.dart` and `wallet_provider.dart` to load demo data:

```dart
// In job_provider.dart fetchJobs()
Future<void> fetchJobs() async {
  _isLoading = true;
  notifyListeners();
  
  // DEMO MODE
  await Future.delayed(Duration(seconds: 1));
  _jobs = DemoData.getDemoJobs();
  _isLoading = false;
  notifyListeners();
  return;
  
  // ... rest of the code
}

// In wallet_provider.dart fetchWallet()
Future<void> fetchWallet() async {
  _isLoading = true;
  notifyListeners();
  
  // DEMO MODE
  await Future.delayed(Duration(seconds: 1));
  _wallet = DemoData.getDemoWallet();
  _isLoading = false;
  notifyListeners();
  return;
  
  // ... rest of the code
}
```

---

## 🔧 Troubleshooting

### ❌ "flutter: command not found"

**Solution**: Flutter not in PATH

**Windows**:
1. Add `C:\src\flutter\bin` to PATH
2. Close and reopen terminal

**macOS/Linux**:
```bash
export PATH="$PATH:$HOME/flutter/bin"
# Add to ~/.bashrc or ~/.zshrc for permanent
```

---

### ❌ "cmdline-tools component is missing"

**Solution**:
1. Open Android Studio
2. Go to: Tools → SDK Manager
3. Click "SDK Tools" tab
4. Check "Android SDK Command-line Tools"
5. Click Apply/OK

---

### ❌ "No devices found"

**Solution**:
1. Start Android emulator (Android Studio → Device Manager → Play button)
2. Wait for emulator to fully boot
3. Run: `flutter devices`
4. Should see emulator listed

**Or for physical device**:
1. Enable USB debugging
2. Connect via USB
3. Accept debugging prompt on phone
4. Run: `flutter devices`

---

### ❌ "Gradle build failed"

**Solution 1** - Clean build:
```bash
cd flutter_app
flutter clean
flutter pub get
flutter run
```

**Solution 2** - Update Gradle:
```bash
cd android
./gradlew clean
cd ..
flutter run
```

**Solution 3** - Check Java version:
```bash
java -version
# Should be Java 11 or higher
```

---

### ❌ "SDK location not found"

**Solution**: Create `android/local.properties`:

**Windows**:
```properties
sdk.dir=C:\\Users\\YourUsername\\AppData\\Local\\Android\\sdk
```

**macOS**:
```properties
sdk.dir=/Users/YourUsername/Library/Android/sdk
```

**Linux**:
```properties
sdk.dir=/home/YourUsername/Android/Sdk
```

---

### ❌ App compiles but shows errors/white screen

**Solution**: Check `flutter doctor`
```bash
flutter doctor -v
```
Fix any issues shown.

---

## 📋 Pre-Flight Checklist

Before running, verify:

```bash
# 1. Flutter installed
flutter --version
# Should show: Flutter 3.x.x

# 2. No issues
flutter doctor
# All items should have ✓ (except optional ones)

# 3. Dependencies installed
cd flutter_app
flutter pub get
# Should complete without errors

# 4. Device available
flutter devices
# Should list at least one device

# 5. Ready to run!
flutter run
```

---

## 🎯 Running Commands

### Basic Run
```bash
cd flutter_app
flutter run
```

### Run on Specific Device
```bash
flutter devices
flutter run -d <device-id>
```

### Run in Release Mode
```bash
flutter run --release
```

### Hot Reload (while app is running)
- Press `r` in terminal → Hot reload
- Press `R` → Hot restart
- Press `q` → Quit

### Build APK
```bash
flutter build apk --release
```
APK location: `build/app/outputs/flutter-apk/app-release.apk`

### Install APK on Connected Device
```bash
flutter install
```

---

## 🔗 Connecting to Backend

If you want to connect to a real backend (not demo mode):

### 1. Start Backend Server
```bash
# In a separate terminal
cd backend
python server.py
# Should start on http://localhost:5000
```

### 2. Configure API URL

Edit `flutter_app/lib/config/api_config.dart`:

**For Android Emulator**:
```dart
static const String baseUrl = 'http://10.0.2.2:5000';
```

**For Physical Device** (same WiFi as your PC):
```dart
// Replace with your computer's IP address
static const String baseUrl = 'http://192.168.1.100:5000';
```

To find your IP:
- **Windows**: `ipconfig` (look for IPv4)
- **macOS**: `ifconfig | grep inet`
- **Linux**: `ip addr show`

### 3. Run the App
```bash
flutter run
```

---

## 📱 Testing the App

### Test Plan:

1. **Launch** → Should see splash screen → Login screen
2. **Login** with demo credentials
3. **Dashboard** → Should show stats and jobs
4. **Jobs Tab** → View today's, upcoming, completed jobs
5. **Click a Job** → See job details
6. **Clock In** (needs location permission)
7. **Update ETA** → Enter custom ETA
8. **Send Message** → Message client
9. **Complete Tasks** → Check off tasks
10. **Clock Out**
11. **Wallet Tab** → View balance and transactions
12. **Payment History** → See all transactions
13. **Profile Tab** → View profile, logout

---

## 🎉 Success Indicators

You've successfully run the app when you see:

✅ App launches without errors
✅ Login screen appears
✅ Can login (demo or real account)
✅ Dashboard shows data
✅ Can navigate between tabs
✅ All screens load properly
✅ No red error screens

---

## 📞 Still Having Issues?

### Check These:

1. **Flutter Version**:
   ```bash
   flutter --version
   # Should be 3.0+
   ```

2. **Flutter Doctor**:
   ```bash
   flutter doctor -v
   # Fix any ✗ issues
   ```

3. **Android Toolchain**:
   - Should show ✓ in `flutter doctor`

4. **Connected Device**:
   ```bash
   flutter devices
   # Should show 1+ devices
   ```

5. **Dependencies**:
   ```bash
   cd flutter_app
   rm -rf pubspec.lock
   flutter pub get
   ```

6. **Clean Rebuild**:
   ```bash
   flutter clean
   flutter pub get
   flutter run
   ```

### Common First-Time Setup Time:
- Flutter installation: 10-15 minutes
- Android Studio setup: 15-20 minutes
- First app build: 5-10 minutes
- **Total: ~30-45 minutes** (one time only)

### Subsequent Runs:
- App startup: 30-60 seconds

---

## 🎊 You're All Set!

Once you see the app running on your device/emulator, you can:

- ✅ Test all features in demo mode
- ✅ Develop new features
- ✅ Customize the UI
- ✅ Connect to your backend
- ✅ Build release APK
- ✅ Deploy to devices

**Happy Flutter Development!** 🚀

---

## 📚 Additional Resources

- **Flutter Docs**: https://flutter.dev/docs
- **Flutter Codelabs**: https://flutter.dev/docs/codelabs
- **Widget Catalog**: https://flutter.dev/docs/development/ui/widgets
- **Flutter YouTube**: https://www.youtube.com/c/flutterdev
- **Pub.dev**: https://pub.dev (Flutter packages)

---

## 🤝 Need More Help?

1. Review `QUICK_START.md`
2. Check `SETUP_INSTRUCTIONS.md`
3. See `FEATURES.md` for feature details
4. Read `APP_ARCHITECTURE.md` for code structure

**The app is ready to run - just install Flutter and go!** 🎯

