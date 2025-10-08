# Flutter Cleaner App - Architecture Overview

## 📐 Application Architecture

### Architecture Pattern: **Provider (MVVM-like)**

```
┌─────────────────────────────────────────────────────────┐
│                      UI LAYER                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │  Screens │  │  Widgets │  │  Dialogs │             │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘             │
│       │             │              │                    │
│       └─────────────┴──────────────┘                    │
│                     │                                   │
├─────────────────────┼───────────────────────────────────┤
│              PROVIDER LAYER                             │
│       ┌─────────────┴─────────────┐                     │
│       │   State Management        │                     │
│  ┌────┴────┐  ┌────────┐  ┌──────┴────┐               │
│  │  Auth   │  │  Job   │  │  Wallet   │               │
│  │Provider │  │Provider│  │ Provider  │               │
│  └────┬────┘  └────┬───┘  └─────┬─────┘               │
│       │            │             │                      │
├───────┼────────────┼─────────────┼──────────────────────┤
│   SERVICE LAYER    │             │                      │
│  ┌────┴────┐  ┌───┴──────┐  ┌───┴────────┐            │
│  │   API   │  │ Location │  │  Storage   │            │
│  │ Service │  │ Service  │  │  Service   │            │
│  └────┬────┘  └────┬─────┘  └─────┬──────┘            │
│       │            │              │                     │
├───────┼────────────┼──────────────┼─────────────────────┤
│   DATA LAYER       │              │                     │
│  ┌────┴────────┐   │         ┌────┴────┐               │
│  │   Backend   │   │         │  Local  │               │
│  │     API     │   │         │ Storage │               │
│  └─────────────┘   │         └─────────┘               │
│               ┌────┴─────┐                              │
│               │   GPS    │                              │
│               │ Hardware │                              │
│               └──────────┘                              │
└─────────────────────────────────────────────────────────┘
```

---

## 🗂️ Folder Structure Explained

### `/lib`
Main application code

#### `/config`
- `api_config.dart` - API endpoints and configuration
  - Base URL
  - All endpoint paths
  - Timeout settings

#### `/models`
Data models representing entities
- `cleaner.dart` - Cleaner/user model
- `job.dart` - Job and Task models
- `payment.dart` - Payment and Wallet models
- `message.dart` - Message model

#### `/services`
Business logic and external integrations
- `api_service.dart` - HTTP client wrapper
  - GET, POST, PUT, DELETE methods
  - Error handling
  - Token management
- `storage_service.dart` - Local data persistence
  - Token storage
  - User data caching
- `location_service.dart` - GPS functionality
  - Get current location
  - Permission handling
  - Distance calculation
  - ETA estimation

#### `/providers`
State management (Provider pattern)
- `auth_provider.dart` - Authentication state
  - Login/logout
  - User session
  - Token management
- `job_provider.dart` - Job state
  - Job list
  - Clock in/out
  - Task management
  - ETA updates
- `wallet_provider.dart` - Wallet state
  - Balance
  - Transactions
  - Earnings

#### `/screens`
UI screens (full pages)

**Auth Screens:**
- `splash_screen.dart` - App loading
- `login_screen.dart` - User login
- `register_screen.dart` - New user registration

**Home Screens:**
- `dashboard_screen.dart` - Main dashboard with tabs

**Job Screens:**
- `jobs_screen.dart` - Job list with tabs
- `job_detail_screen.dart` - Individual job details

**Wallet Screens:**
- `wallet_screen.dart` - Wallet overview
- `payment_history_screen.dart` - Transaction history

**Profile Screens:**
- `profile_screen.dart` - User profile and settings

#### `/widgets`
Reusable UI components
- `job_card.dart` - Job list item
- `dashboard_stats_card.dart` - Stat display card

#### `/utils`
Utility classes and helpers
- `demo_data.dart` - Mock data for testing

---

## 🔄 Data Flow

### Example: User Login Flow

```
1. User enters credentials
   ↓
2. LoginScreen captures input
   ↓
3. Calls AuthProvider.login()
   ↓
4. AuthProvider calls ApiService.post()
   ↓
5. ApiService makes HTTP request to backend
   ↓
6. Backend responds with token + user data
   ↓
7. StorageService saves token locally
   ↓
8. AuthProvider updates currentUser state
   ↓
9. UI rebuilds (notifyListeners())
   ↓
10. Navigate to DashboardScreen
```

### Example: Clock In Flow

```
1. User taps "Clock In" on JobDetailScreen
   ↓
2. LocationService.getCurrentLocation()
   ↓
3. Request location permission
   ↓
4. Get GPS coordinates
   ↓
5. JobProvider.clockIn(jobId)
   ↓
6. ApiService.post() with location data
   ↓
7. Backend updates job status
   ↓
8. JobProvider updates job in list
   ↓
9. UI rebuilds to show "In Progress"
   ↓
10. Show clock out button
```

---

## 🎯 State Management Pattern

### Provider Pattern

**Benefits:**
- ✅ Simple to understand
- ✅ Built-in with Flutter
- ✅ Efficient rebuilds
- ✅ Testable
- ✅ Scalable

**Structure:**
```dart
class AuthProvider extends ChangeNotifier {
  // State
  Cleaner? _currentUser;
  bool _isLoading = false;
  
  // Getters
  Cleaner? get currentUser => _currentUser;
  bool get isLoading => _isLoading;
  
  // Methods
  Future<bool> login(String email, String password) async {
    _isLoading = true;
    notifyListeners(); // UI rebuilds
    
    // API call
    final result = await _apiService.post(...);
    
    _currentUser = result;
    _isLoading = false;
    notifyListeners(); // UI rebuilds
  }
}
```

**Usage in UI:**
```dart
Consumer<AuthProvider>(
  builder: (context, authProvider, child) {
    if (authProvider.isLoading) {
      return CircularProgressIndicator();
    }
    return Text(authProvider.currentUser.name);
  },
)
```

---

## 🔐 Security Architecture

### Authentication Flow
```
┌──────────┐      Token      ┌──────────┐
│  Client  │ ───────────────> │ Backend  │
│   App    │                  │   API    │
└──────────┘                  └──────────┘
     │                             │
     │ 1. Login (email/password)   │
     │ ─────────────────────────>  │
     │                             │
     │ 2. JWT Token + User Data    │
     │ <─────────────────────────  │
     │                             │
     │ 3. Store Token Locally      │
     │ (Secure Storage)            │
     │                             │
     │ 4. All requests include     │
     │    Authorization header     │
     │ ─────────────────────────>  │
     │                             │
     │ 5. Token validated          │
     │    Response sent            │
     │ <─────────────────────────  │
```

### Data Security
- **Local Storage**: Encrypted (flutter_secure_storage for sensitive data)
- **Network**: HTTPS ready
- **Tokens**: Stored securely
- **Validation**: All inputs validated

---

## 📊 Navigation Architecture

```
SplashScreen
     │
     ├─ Authenticated? Yes ──> DashboardScreen (Bottom Nav)
     │                              │
     │                              ├─ Home Tab
     │                              ├─ Jobs Tab ──> JobDetailScreen
     │                              ├─ Wallet Tab ──> PaymentHistoryScreen
     │                              └─ Profile Tab
     │
     └─ Authenticated? No ──> LoginScreen
                                   │
                                   └─> RegisterScreen
```

### Bottom Navigation Tabs
```
┌────────────────────────────────────────┐
│              App Bar                   │
├────────────────────────────────────────┤
│                                        │
│          Tab Content                   │
│      (Switched based on                │
│       selected tab)                    │
│                                        │
├────────────────────────────────────────┤
│  [Home] [Jobs] [Wallet] [Profile]     │
└────────────────────────────────────────┘
```

---

## 🧩 Component Relationships

### Dashboard Screen Structure
```
DashboardScreen
└── BottomNavigationBar
    ├── Tab 0: DashboardHome
    │   ├── WelcomeCard
    │   ├── StatsCards (4)
    │   │   └── DashboardStatsCard
    │   └── TodayJobsList
    │       └── JobCard (multiple)
    │
    ├── Tab 1: JobsScreen
    │   ├── TabBar (3 tabs)
    │   └── TabBarView
    │       └── JobCard (multiple)
    │           └── → JobDetailScreen
    │
    ├── Tab 2: WalletScreen
    │   ├── BalanceCard
    │   ├── QuickActions
    │   └── RecentTransactions
    │       └── → PaymentHistoryScreen
    │
    └── Tab 3: ProfileScreen
        ├── ProfileHeader
        ├── ContactInfo
        ├── Statistics
        └── Settings
```

---

## 🔌 API Integration Architecture

### HTTP Service Layer
```dart
ApiService
├── _getHeaders() - Add auth token
├── get(endpoint) - GET request
├── post(endpoint, body) - POST request
├── put(endpoint, body) - PUT request
├── delete(endpoint) - DELETE request
└── _handleResponse() - Parse & error handling
```

### Request Flow
```
Provider Method
      ↓
ApiService.post('/endpoint', data)
      ↓
Add Authorization Header
      ↓
HTTP POST Request
      ↓
Backend API
      ↓
JSON Response
      ↓
Parse Response
      ↓
Error Handling
      ↓
Return Data
      ↓
Update Provider State
      ↓
notifyListeners()
      ↓
UI Rebuilds
```

---

## 📱 Platform-Specific Architecture

### Android
```
android/
├── app/
│   ├── build.gradle          # Build configuration
│   └── src/main/
│       ├── AndroidManifest.xml  # Permissions, app config
│       ├── kotlin/
│       │   └── MainActivity.kt  # Entry point
│       └── res/              # Resources (icons, etc.)
└── build.gradle             # Project-level config
```

### iOS (Ready for development)
```
ios/
├── Runner/
│   ├── Info.plist           # App configuration
│   └── AppDelegate.swift    # Entry point
└── Podfile                  # Dependencies
```

---

## 🎨 UI Component Hierarchy

### Material Design Structure
```
MaterialApp
└── Theme
    └── Routes
        └── Scaffold
            ├── AppBar
            ├── Body (Screen Content)
            │   └── SingleChildScrollView
            │       └── Column/ListView
            │           └── Cards
            │               └── Content Widgets
            └── BottomNavigationBar
```

### Common Widget Pattern
```dart
Scaffold(
  appBar: AppBar(...),
  body: RefreshIndicator(
    onRefresh: () async => fetchData(),
    child: SingleChildScrollView(
      child: Column(
        children: [
          Card(...),
          Card(...),
          ListView.builder(...)
        ]
      )
    )
  )
)
```

---

## 🔧 Build & Deployment Architecture

### Development Build
```
flutter run
    ↓
Debug Mode
    ↓
Hot Reload Enabled
    ↓
Development Features Active
```

### Production Build
```
flutter build apk --release
    ↓
Release Mode
    ↓
Code Optimized & Minified
    ↓
APK Generated
    ↓
Ready for Distribution
```

---

## 📈 Scalability Considerations

### Current Architecture Supports:
- ✅ Multiple cleaners (multi-user)
- ✅ Unlimited jobs
- ✅ Unlimited transactions
- ✅ Easy feature additions
- ✅ Backend changes (just update API endpoints)
- ✅ New screens (add to navigation)
- ✅ New providers (add to MultiProvider)

### Future Enhancements Possible:
- Push notifications
- Offline mode (local database)
- Real-time updates (WebSocket)
- File uploads
- Multi-language support
- Dark mode theme
- Advanced analytics

---

## 🎯 Design Patterns Used

1. **Provider Pattern**: State management
2. **Repository Pattern**: API service abstraction
3. **Singleton Pattern**: Service instances
4. **Factory Pattern**: Model fromJson()
5. **Observer Pattern**: ChangeNotifier/Listeners
6. **Dependency Injection**: Providers

---

## 📊 Performance Optimization

### Implemented:
- ✅ Lazy loading lists
- ✅ Efficient rebuilds (Consumer widgets)
- ✅ Image optimization (assets)
- ✅ Async operations
- ✅ Proper widget disposal
- ✅ Const constructors where possible

### Best Practices:
- Using `const` constructors
- ListView.builder for long lists
- Proper async/await usage
- Resource disposal in dispose()
- Minimal widget rebuilds

---

This architecture ensures:
- 📱 **Maintainability**: Clean, organized code
- ⚡ **Performance**: Optimized rendering
- 🔒 **Security**: Secure data handling
- 📈 **Scalability**: Easy to extend
- 🎨 **User Experience**: Smooth, responsive UI

