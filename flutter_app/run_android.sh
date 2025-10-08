#!/bin/bash

echo "======================================"
echo "Flutter Cleaner App - Android Runner"
echo "======================================"
echo ""

# Check if Flutter is installed
if ! command -v flutter &> /dev/null
then
    echo "❌ Flutter is not installed or not in PATH"
    echo "Please install Flutter from: https://flutter.dev/docs/get-started/install"
    exit 1
fi

echo "✅ Flutter found: $(flutter --version | head -n 1)"
echo ""

# Run Flutter doctor
echo "Checking Flutter installation..."
flutter doctor
echo ""

# Get dependencies
echo "Getting dependencies..."
flutter pub get
echo ""

# Check for connected devices
echo "Checking for connected devices..."
flutter devices
echo ""

# Ask user to continue
read -p "Do you want to run the app now? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "Starting the app..."
    flutter run
else
    echo "Setup complete. Run 'flutter run' when ready."
fi

