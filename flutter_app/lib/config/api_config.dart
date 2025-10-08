class ApiConfig {
  // Update this URL to point to your backend server
  static const String baseUrl = 'http://10.0.2.2:8000'; // Android emulator localhost (backend on port 8000)
  // For physical device, use: 'http://YOUR_IP_ADDRESS:8001'

  // API Endpoints
  static const String loginEndpoint = '/api/auth/login';
  static const String registerEndpoint = '/api/cleaner/register';
  static const String jobsEndpoint = '/api/cleaner/jobs';
  static const String clockInEndpoint = '/api/cleaner/clock-in';
  static const String clockOutEndpoint = '/api/cleaner/clock-out';
  static const String updateEtaEndpoint = '/api/cleaner/update-eta';
  static const String sendMessageEndpoint = '/api/cleaner/send-message';
  static const String earningsEndpoint = '/api/cleaner/earnings';
  static const String walletEndpoint = '/api/cleaner/wallet';
  static const String paymentsEndpoint = '/api/cleaner/payments';
  static const String profileEndpoint = '/api/cleaner/profile';
  static const String calendarEndpoint = '/api/cleaner/calendar';
  static const String calendarEventsEndpoint = '/api/cleaner/calendar/events';

  // Request timeout
  static const Duration timeout = Duration(seconds: 30);
}

