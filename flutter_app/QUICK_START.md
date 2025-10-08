# Quick Start Guide - Flutter Cleaner App

## 🚀 Getting Started in 5 Minutes

### Step 1: Install Flutter

#### Windows:
1. Download Flutter SDK: https://docs.flutter.dev/get-started/install/windows
2. Extract to `C:\src\flutter`
3. Add to PATH: `C:\src\flutter\bin`
4. Restart terminal

#### macOS:
```bash
# Using Homebrew
brew install flutter

# Or download directly
# https://docs.flutter.dev/get-started/install/macos
```

#### Linux:
```bash
# Download and extract Flutter
wget https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_3.16.0-stable.tar.xz
tar xf flutter_linux_3.16.0-stable.tar.xz
export PATH="$PATH:`pwd`/flutter/bin"
```

### Step 2: Verify Installation

```bash
flutter doctor
```

Accept Android licenses if prompted:
```bash
flutter doctor --android-licenses
```

### Step 3: Set Up Android Device

**Option A: Use Android Emulator (Recommended)**
1. Open Android Studio
2. Go to Tools → Device Manager
3. Create a new Virtual Device
4. Select a device (e.g., Pixel 5)
5. Download a system image (e.g., Android 13)
6. Start the emulator

**Option B: Use Physical Device**
1. Enable Developer Mode on your Android phone
2. Enable USB Debugging
3. Connect via USB
4. Verify: `flutter devices`

### Step 4: Run the App

```bash
cd flutter_app
flutter pub get
flutter run
```

## 📱 Running on Android (Detailed)

### First Time Setup

```bash
# Navigate to flutter_app directory
cd flutter_app

# Install dependencies
flutter pub get

# Check available devices
flutter devices

# Run on default device
flutter run

# Or specify a device
flutter run -d <device-id>
```

### Using the Batch File (Windows)

```cmd
# Double-click run_android.bat
# Or run from command prompt:
run_android.bat
```

### Using the Shell Script (macOS/Linux)

```bash
chmod +x run_android.sh
./run_android.sh
```

## 🎮 Demo Mode (No Backend Required)

The app includes demo data for testing without a backend server.

### Enable Demo Mode:

Edit `lib/providers/auth_provider.dart` and add demo login:

```dart
Future<bool> login(String email, String password) async {
  // Demo mode - comment out for production
  if (email == 'demo@example.com' && password == 'demo123') {
    _currentUser = DemoData.getDemoCleaner();
    await _storageService.saveUser(_currentUser!);
    return true;
  }
  // Rest of the code...
}
```

### Demo Credentials:
- **Email**: demo@example.com
- **Password**: demo123

## 🔧 Common Issues & Solutions

### Issue: "Flutter not found"
**Solution**: Add Flutter to your system PATH
- Windows: Add `C:\src\flutter\bin` to PATH
- macOS/Linux: Add `export PATH="$PATH:/path/to/flutter/bin"` to `.bashrc` or `.zshrc`

### Issue: "Android licenses not accepted"
**Solution**: 
```bash
flutter doctor --android-licenses
```

### Issue: "No devices found"
**Solution**: 
- Start Android emulator from Android Studio
- Or connect physical device with USB debugging enabled
- Verify with: `flutter devices`

### Issue: "Gradle build failed"
**Solution**:
```bash
cd android
./gradlew clean
cd ..
flutter clean
flutter pub get
flutter run
```

### Issue: "SDK location not found"
**Solution**: Create `android/local.properties`:
```properties
sdk.dir=C:\\Users\\YourUsername\\AppData\\Local\\Android\\sdk
# or on macOS/Linux
sdk.dir=/Users/YourUsername/Library/Android/sdk
```

## 📋 Pre-Run Checklist

Before running the app, ensure:

- ✅ Flutter SDK installed (`flutter --version` works)
- ✅ Android Studio installed with Android SDK
- ✅ At least one device available (`flutter devices` shows a device)
- ✅ Dependencies installed (`flutter pub get` completed)
- ✅ No errors in `flutter doctor`

## 🎯 Build & Install APK

### Build APK:
```bash
flutter build apk --release
```

The APK will be at: `build/app/outputs/flutter-apk/app-release.apk`

### Install APK on device:
```bash
flutter install
```

Or manually:
1. Copy `app-release.apk` to your phone
2. Enable "Install from Unknown Sources"
3. Tap the APK to install

## 🌐 Backend Integration

### Without Backend (Demo Mode):
The app works standalone with demo data - perfect for testing!

### With Backend:
1. Update `lib/config/api_config.dart`:
   ```dart
   // Android Emulator
   static const String baseUrl = 'http://10.0.2.2:5000';
   
   // Physical Device (use your PC's IP)
   static const String baseUrl = 'http://192.168.1.XXX:5000';
   ```

2. Start backend server:
   ```bash
   cd ../backend
   python server.py
   ```

3. Ensure your phone and PC are on the same WiFi network

## 🎨 App Features

Once running, you'll have access to:

1. **Login/Register** - Multi-user authentication
2. **Dashboard** - Overview of jobs and earnings
3. **Jobs Tab** - View today's, upcoming, and completed jobs
4. **Job Details** - Clock in/out, update ETA, message clients
5. **Wallet** - Track earnings and payment history
6. **Profile** - View stats and settings

## 📞 Support

Need help?
1. Check `flutter doctor` for setup issues
2. Review `SETUP_INSTRUCTIONS.md` for detailed steps
3. See Flutter docs: https://flutter.dev/docs

## 🚦 Next Steps

After successful setup:
1. Explore the demo mode to understand features
2. Connect to your backend API
3. Customize the app for your needs
4. Build and deploy to your team

Happy coding! 🎉

