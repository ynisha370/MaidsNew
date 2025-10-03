import 'package:flutter/material.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'api_service.dart';

class NotificationService extends ChangeNotifier {
  final ApiService _apiService;
  final FirebaseMessaging _firebaseMessaging = FirebaseMessaging.instance;
  
  String? _fcmToken;
  bool _isInitialized = false;
  String? _errorMessage;
  
  NotificationService(this._apiService);
  
  // Getters
  String? get fcmToken => _fcmToken;
  bool get isInitialized => _isInitialized;
  String? get errorMessage => _errorMessage;
  
  // Initialize notifications
  Future<void> initialize() async {
    if (_isInitialized) return;
    
    try {
      // Request permission
      final settings = await _firebaseMessaging.requestPermission(
        alert: true,
        badge: true,
        sound: true,
      );
      
      if (settings.authorizationStatus == AuthorizationStatus.authorized) {
        // Get FCM token
        _fcmToken = await _firebaseMessaging.getToken();
        
        // Save token to preferences
        if (_fcmToken != null) {
          final prefs = await SharedPreferences.getInstance();
          await prefs.setString('fcm_token', _fcmToken!);
        }
        
        // Set up message handlers
        _setupMessageHandlers();
        
        _isInitialized = true;
        notifyListeners();
      } else {
        _setError('Notification permission denied');
      }
    } catch (e) {
      _setError('Failed to initialize notifications: ${e.toString()}');
    }
  }
  
  // Set up message handlers
  void _setupMessageHandlers() {
    // Handle foreground messages
    FirebaseMessaging.onMessage.listen((RemoteMessage message) {
      _handleForegroundMessage(message);
    });
    
    // Handle background messages
    FirebaseMessaging.onMessageOpenedApp.listen((RemoteMessage message) {
      _handleBackgroundMessage(message);
    });
    
    // Handle terminated app messages
    _firebaseMessaging.getInitialMessage().then((RemoteMessage? message) {
      if (message != null) {
        _handleBackgroundMessage(message);
      }
    });
  }
  
  // Handle foreground messages
  void _handleForegroundMessage(RemoteMessage message) {
    // Show local notification or update UI
    print('Received foreground message: ${message.notification?.title}');
    
    // You can show a snackbar or update the UI here
    // For now, we'll just print the message
  }
  
  // Handle background messages
  void _handleBackgroundMessage(RemoteMessage message) {
    print('Received background message: ${message.notification?.title}');
    
    // Handle navigation based on message data
    final data = message.data;
    if (data.containsKey('route')) {
      // Navigate to specific route
      // This would be handled by the main app
    }
  }
  
  // Send local notification
  Future<void> sendLocalNotification({
    required String title,
    required String body,
    String? payload,
  }) async {
    // In a real implementation, you would use flutter_local_notifications
    // For now, we'll just show a debug message
    print('Local notification: $title - $body');
  }
  
  // Send notification to customer
  Future<bool> sendCustomerNotification(String customerId, String message) async {
    try {
      final result = await _apiService.sendCustomerNotification(customerId, message);
      
      if (result['success']) {
        _clearError();
        return true;
      } else {
        _setError(result['error']);
        return false;
      }
    } catch (e) {
      _setError('Failed to send notification: ${e.toString()}');
      return false;
    }
  }
  
  // Subscribe to topic
  Future<void> subscribeToTopic(String topic) async {
    try {
      await _firebaseMessaging.subscribeToTopic(topic);
      print('Subscribed to topic: $topic');
    } catch (e) {
      _setError('Failed to subscribe to topic: ${e.toString()}');
    }
  }
  
  // Unsubscribe from topic
  Future<void> unsubscribeFromTopic(String topic) async {
    try {
      await _firebaseMessaging.unsubscribeFromTopic(topic);
      print('Unsubscribed from topic: $topic');
    } catch (e) {
      _setError('Failed to unsubscribe from topic: ${e.toString()}');
    }
  }
  
  // Get stored FCM token
  Future<String?> getStoredToken() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      return prefs.getString('fcm_token');
    } catch (e) {
      _setError('Failed to get stored token: ${e.toString()}');
      return null;
    }
  }
  
  // Clear stored token
  Future<void> clearStoredToken() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove('fcm_token');
      _fcmToken = null;
      notifyListeners();
    } catch (e) {
      _setError('Failed to clear stored token: ${e.toString()}');
    }
  }
  
  // Helper methods
  void _setError(String error) {
    _errorMessage = error;
    notifyListeners();
  }
  
  void _clearError() {
    _errorMessage = null;
  }
  
  void clearError() {
    _clearError();
    notifyListeners();
  }
}
