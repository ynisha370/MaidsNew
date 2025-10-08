# Flutter Cleaner App - Setup Instructions

## Prerequisites

1. **Flutter SDK**: Install Flutter 3.0.0 or higher
   - Download from: https://flutter.dev/docs/get-started/install
   - Verify installation: `flutter doctor`

2. **Android Studio** (for Android development)
   - Download from: https://developer.android.com/studio
   - Install Android SDK and Android Virtual Device (AVD)

3. **Xcode** (for iOS development - macOS only)
   - Install from Mac App Store
   - Run: `sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer`

## Setup Steps

### 1. Install Dependencies

```bash
cd flutter_app
flutter pub get
```

### 2. Configure Backend API

Edit `lib/config/api_config.dart` and update the `baseUrl`:

```dart
// For Android Emulator (localhost backend)
static const String baseUrl = 'http://10.0.2.2:5000';

// For physical Android device (replace with your computer's IP)
static const String baseUrl = 'http://192.168.1.100:5000';

// For iOS Simulator
static const String baseUrl = 'http://localhost:5000';
```

### 3. Android Setup

#### Check connected devices/emulators:
```bash
flutter devices
```

#### Start an Android emulator:
```bash
# List available emulators
flutter emulators

# Launch an emulator
flutter emulators --launch <emulator_id>
```

#### Run on Android:
```bash
flutter run
```

### 4. iOS Setup (macOS only)

```bash
# Install CocoaPods dependencies
cd ios
pod install
cd ..

# Run on iOS
flutter run -d ios
```

## Running the App

### Quick Start (Android)

```bash
# Make sure you're in the flutter_app directory
cd flutter_app

# Get dependencies
flutter pub get

# Run the app
flutter run
```

### Build for Release

#### Android APK:
```bash
flutter build apk --release
# Output: build/app/outputs/flutter-apk/app-release.apk
```

#### Android App Bundle (for Play Store):
```bash
flutter build appbundle --release
# Output: build/app/outputs/bundle/release/app-release.aab
```

#### iOS (macOS only):
```bash
flutter build ios --release
```

## Demo Mode

The app includes demo data for testing without a backend:

1. Uncomment the demo data in providers (auth_provider.dart, job_provider.dart, wallet_provider.dart)
2. Use demo credentials:
   - Email: demo@example.com
   - Password: demo123

## Troubleshooting

### Common Issues

1. **"flutter: command not found"**
   - Add Flutter to PATH: `export PATH="$PATH:`pwd`/flutter/bin"`

2. **Android licenses not accepted**
   ```bash
   flutter doctor --android-licenses
   ```

3. **Gradle build errors**
   ```bash
   cd android
   ./gradlew clean
   cd ..
   flutter clean
   flutter pub get
   ```

4. **iOS pod install errors**
   ```bash
   cd ios
   pod repo update
   pod install
   cd ..
   ```

5. **Hot reload not working**
   - Press `r` in terminal for hot reload
   - Press `R` for hot restart
   - Press `q` to quit

## Development Tips

1. **Enable hot reload**: The app supports hot reload - just save your changes!

2. **Debug mode**: Run with `flutter run --debug`

3. **Check logs**: 
   ```bash
   flutter logs
   ```

4. **Clean build**:
   ```bash
   flutter clean
   flutter pub get
   flutter run
   ```

## Backend Integration

To connect to your backend:

1. Start your backend server (from the project root):
   ```bash
   cd backend
   python server.py
   ```

2. Update `lib/config/api_config.dart` with your backend URL

3. Ensure your backend has the following endpoints:
   - POST `/api/cleaner/login`
   - POST `/api/cleaner/register`
   - GET `/api/cleaner/jobs`
   - POST `/api/cleaner/clock-in`
   - POST `/api/cleaner/clock-out`
   - POST `/api/cleaner/update-eta`
   - POST `/api/cleaner/send-message`
   - GET `/api/cleaner/wallet`
   - GET `/api/cleaner/payments`
   - GET `/api/cleaner/earnings`

## Features Implemented

✅ Multi-user authentication
✅ Job viewing and management
✅ Clock in/out functionality
✅ Task assignment and tracking
✅ ETA updates
✅ Client communication
✅ Digital wallet
✅ Earnings tracking
✅ Payment history
✅ Cleaner dashboard
✅ Profile management

## Support

For issues or questions, refer to:
- Flutter documentation: https://flutter.dev/docs
- Stack Overflow: https://stackoverflow.com/questions/tagged/flutter

