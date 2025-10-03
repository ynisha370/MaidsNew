# Maids of Cyfair - Cleaner Mobile App

A comprehensive Flutter mobile application for cleaners to manage their assigned jobs, track time, communicate with customers, and document their work.

## 🚀 Features

### 🔐 Authentication & Security
- Secure login system for cleaners
- JWT token management with automatic refresh
- Demo credentials for testing
- Role-based access control

### 📱 Job Management
- View assigned jobs (today, upcoming, completed)
- Detailed job information with customer data
- Real-time job status updates
- Interactive job checklist with progress tracking
- Service details and pricing information

### ⏰ Time Tracking & Productivity
- Clock in/out functionality with GPS verification
- Real-time work duration tracking
- Animated job timer with visual indicators
- Work summary reports and analytics
- Location-based job verification

### 📋 Interactive Checklist System
- Dynamic checklist based on job type and services
- Mark tasks as completed with timestamps
- Progress percentage calculation
- Required vs optional task differentiation
- Custom checklist items for a-la-carte services

### 📸 Photo Documentation
- Take photos during job execution
- Before/after photo capture
- Photo gallery with grid view
- Automatic photo upload to server
- Photo management and deletion

### 📍 Location Services & Navigation
- GPS location tracking
- Distance calculation to job sites
- Integrated navigation (Google Maps)
- Location-based job verification
- Real-time location updates

### 💬 Customer Communication
- Direct phone calling to customers
- SMS messaging capabilities
- ETA updates and notifications
- Progress updates and completion notifications
- Customer information display

### 🔔 Push Notifications
- Firebase Cloud Messaging integration
- Real-time job updates
- Customer notification system
- Background message handling
- Notification preferences

### 📊 Performance Dashboard
- Job statistics and metrics
- Completion rates and ratings
- Work history and analytics
- Performance tracking
- Cleaner profile management

### 🌐 Offline Support
- Offline data storage and sync
- Pending updates queue
- Network connectivity monitoring
- Automatic data synchronization
- Offline job management

## 🛠 Tech Stack

- **Framework**: Flutter 3.0+
- **State Management**: Provider
- **HTTP Client**: HTTP & Dio
- **Local Storage**: SharedPreferences
- **Database**: MongoDB (via API)
- **Authentication**: JWT tokens
- **Location**: Geolocator
- **Camera**: Image Picker
- **Notifications**: Firebase Cloud Messaging
- **Navigation**: Google Maps integration
- **UI Components**: Material Design 3
- **Animations**: Custom animations with AnimationController

## 📁 Architecture

```
lib/
├── main.dart                     # App entry point with providers
├── models/                       # Data models
│   ├── cleaner.dart             # Cleaner profile model
│   ├── job.dart                 # Job and checklist models
│   └── customer.dart            # Customer information model
├── services/                    # Business logic services
│   ├── api_service.dart         # HTTP API communication
│   ├── auth_service.dart        # Authentication management
│   ├── job_service.dart         # Job operations
│   ├── customer_service.dart    # Customer data management
│   ├── photo_service.dart       # Photo documentation
│   ├── location_service.dart    # GPS and navigation
│   ├── notification_service.dart # Push notifications
│   └── offline_service.dart     # Offline data management
├── screens/                     # UI screens
│   ├── splash_screen.dart      # Animated splash screen
│   ├── login_screen.dart       # Authentication
│   ├── home_screen.dart        # Main dashboard
│   └── job_detail_screen.dart  # Detailed job view
├── widgets/                     # Reusable UI components
│   ├── job_card.dart           # Job list item
│   ├── stats_card.dart         # Statistics display
│   ├── checklist_item_widget.dart # Checklist items
│   ├── job_timer_widget.dart   # Time tracking
│   ├── location_widget.dart    # Location and navigation
│   └── notification_widget.dart # Customer communication
└── utils/                       # Utilities
    └── app_theme.dart          # Theme configuration
```

## 🔧 Setup & Installation

### Prerequisites
- Flutter SDK (3.0+)
- Dart SDK
- Android Studio / VS Code
- Android/iOS development environment

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd cleaner_app
   ```

2. **Install dependencies**
   ```bash
   flutter pub get
   ```

3. **Configure Firebase** (for notifications)
   - Add `google-services.json` (Android)
   - Add `GoogleService-Info.plist` (iOS)

4. **Update API endpoints**
   - Modify `api_service.dart` with your backend URL
   - Update authentication endpoints if needed

5. **Run the app**
   ```bash
   flutter run
   ```

## 🎯 Key Features Implementation

### Authentication Flow
- Secure login with JWT tokens
- Automatic token refresh
- Role-based access (cleaner only)
- Demo credentials for testing

### Job Management
- Real-time job updates
- Status tracking (pending → confirmed → in_progress → completed)
- Customer information display
- Service details and pricing

### Time Tracking
- GPS-verified clock in/out
- Real-time duration tracking
- Work summary reports
- Location-based verification

### Photo Documentation
- Camera integration
- Gallery photo selection
- Automatic photo upload
- Photo management and organization

### Location Services
- GPS location tracking
- Distance calculation
- Navigation integration
- Location-based job verification

### Customer Communication
- Direct phone calling
- SMS messaging
- ETA updates
- Progress notifications

### Offline Support
- Local data storage
- Pending updates queue
- Network monitoring
- Automatic synchronization

## 🔐 Security Features

- JWT token authentication
- Secure API communication
- Location permission handling
- Camera permission management
- Data encryption for sensitive information

## 📱 Platform Support

- **Android**: API level 21+ (Android 5.0+)
- **iOS**: iOS 11.0+
- **Responsive Design**: Optimized for various screen sizes
- **Accessibility**: Screen reader support and accessibility features

## 🚀 Performance Optimizations

- Lazy loading of images
- Efficient state management
- Background task handling
- Memory management
- Network optimization

## 🧪 Testing

### Demo Credentials
- **Email**: cleaner@maids.com
- **Password**: cleaner123

### Test Features
- Job assignment and management
- Time tracking and clock in/out
- Photo documentation
- Customer communication
- Location services
- Offline functionality

## 📈 Future Enhancements

- [ ] Advanced analytics dashboard
- [ ] Team collaboration features
- [ ] Advanced reporting
- [ ] Integration with calendar apps
- [ ] Voice notes and recording
- [ ] Advanced photo editing
- [ ] Multi-language support
- [ ] Dark mode theme

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support and questions:
- Email: support@maidsofcyfair.com
- Documentation: [Link to documentation]
- Issues: [GitHub Issues]

---

**Built with ❤️ for Maids of Cyfair**