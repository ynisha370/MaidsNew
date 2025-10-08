# Cleaner App

A comprehensive Flutter application for cleaners to manage their daily tasks, track earnings, and communicate with clients.

## Features

- **Multi-user Authentication**: Support for multiple cleaner logins
- **Job Management**: View assigned jobs and tasks
- **Clock In/Out**: Track working hours with geolocation
- **ETA Updates**: Send real-time updates to clients
- **Client Communication**: Direct messaging with clients
- **Earnings Dashboard**: View earnings and payment history
- **Digital Wallet**: Manage payments and withdrawals
- **Payment History**: Track all transactions

## Setup Instructions

### Prerequisites

- Flutter SDK (3.0.0 or higher)
- Android Studio / Xcode
- Android device or emulator

### Installation

1. Clone the repository
2. Navigate to the flutter_app directory
3. Run `flutter pub get` to install dependencies
4. Configure the backend API URL in `lib/config/api_config.dart`
5. Run the app:
   - Android: `flutter run`
   - iOS: `flutter run -d ios`

### Android Setup

1. Ensure Android SDK is installed
2. Connect an Android device or start an emulator
3. Run `flutter run`

### iOS Setup

1. Ensure Xcode is installed (macOS only)
2. Run `pod install` in the ios directory
3. Open the project in Xcode and configure signing
4. Run `flutter run -d ios`

## Project Structure

```
lib/
├── main.dart                 # App entry point
├── config/                   # Configuration files
├── models/                   # Data models
├── services/                 # API and business logic
├── providers/                # State management
├── screens/                  # UI screens
├── widgets/                  # Reusable widgets
└── utils/                    # Utility functions
```

## Backend Integration

This app requires a backend API. Update the API URL in `lib/config/api_config.dart` to point to your server.

## License

MIT License

