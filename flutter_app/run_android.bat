@echo off
echo ======================================
echo Flutter Cleaner App - Android Runner
echo ======================================
echo.

REM Check if Flutter is installed
where flutter >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Flutter is not installed or not in PATH
    echo Please install Flutter from: https://flutter.dev/docs/get-started/install
    pause
    exit /b 1
)

echo Flutter found
flutter --version
echo.

REM Run Flutter doctor
echo Checking Flutter installation...
flutter doctor
echo.

REM Get dependencies
echo Getting dependencies...
flutter pub get
echo.

REM Check for connected devices
echo Checking for connected devices...
flutter devices
echo.

REM Ask user to continue
set /p confirm=Do you want to run the app now? (y/n): 
if /i "%confirm%"=="y" (
    echo Starting the app...
    flutter run
) else (
    echo Setup complete. Run 'flutter run' when ready.
)

pause

