#!/bin/bash

echo "============================================================"
echo "  Flutter Cleaner App - Android Emulator Launcher"
echo "============================================================"
echo ""

# Check if Flutter is installed
if ! command -v flutter &> /dev/null; then
    echo "[ERROR] Flutter is not installed or not in PATH"
    echo ""
    echo "Please install Flutter first:"
    echo "1. Read INSTALL_FLUTTER_AND_RUN.md for complete guide"
    echo "2. Download Flutter from: https://flutter.dev/"
    echo "3. Extract to ~/flutter"
    echo "4. Add to PATH: export PATH=\"\$PATH:\$HOME/flutter/bin\""
    echo "5. Run this script again"
    echo ""
    exit 1
fi

echo "[OK] Flutter found"
flutter --version
echo ""

# Check for Flutter app directory
if [ ! -f "flutter_app/pubspec.yaml" ]; then
    echo "[ERROR] flutter_app directory not found"
    echo "Please run this script from the project root directory"
    exit 1
fi

echo "[OK] Flutter app found"
echo ""

# Navigate to Flutter app
cd flutter_app

# Check dependencies
echo "Checking dependencies..."
flutter pub get
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to get dependencies"
    exit 1
fi
echo "[OK] Dependencies ready"
echo ""

# Check for connected devices
echo "Checking for connected devices..."
flutter devices
if [ $? -ne 0 ]; then
    echo "[WARNING] No devices detected"
    echo ""
    echo "Please ensure:"
    echo "1. Android Studio is installed"
    echo "2. An Android emulator is created"
    echo "3. The emulator is running (started from Android Studio)"
    echo ""
    echo "To create and start an emulator:"
    echo "1. Open Android Studio"
    echo "2. Go to: Tools -> Device Manager"
    echo "3. Click \"Create Device\""
    echo "4. Select Pixel 5, download system image, finish"
    echo "5. Click Play button to start emulator"
    echo "6. Wait for emulator to fully boot"
    echo "7. Run this script again"
    echo ""
    exit 1
fi
echo ""

# Ask user to continue
echo "============================================================"
echo "  Ready to launch app on emulator!"
echo "============================================================"
echo ""
echo "Backend Status: Should be running on http://localhost:8000"
echo "API Endpoint:   http://10.0.2.2:8000 (configured for emulator)"
echo ""
echo "Login Credentials:"
echo "  Email:    cleaner@maids.com"
echo "  Password: cleaner123"
echo ""
read -p "Do you want to launch the app now? (y/n): " confirm

if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "Cancelled."
    cd ..
    exit 0
fi

echo ""
echo "============================================================"
echo "  Launching app on emulator..."
echo "  (First run may take 2-5 minutes to compile)"
echo "============================================================"
echo ""
echo "While app is running:"
echo "  Press 'r' for hot reload"
echo "  Press 'R' for hot restart"
echo "  Press 'q' to quit"
echo "  Press 'h' for help"
echo ""

# Run the app
flutter run

# Return to root directory
cd ..

echo ""
echo "============================================================"
echo "  App session ended"
echo "============================================================"

