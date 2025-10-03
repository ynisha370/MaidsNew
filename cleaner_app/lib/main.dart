import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'services/api_service.dart';
import 'services/auth_service.dart';
import 'services/job_service.dart';
import 'services/customer_service.dart';
import 'services/photo_service.dart';
import 'services/location_service.dart';
import 'services/notification_service.dart';
import 'services/offline_service.dart';
import 'screens/splash_screen.dart';
import 'screens/login_screen.dart';
import 'screens/home_screen.dart';
import 'screens/job_detail_screen.dart';
import 'utils/app_theme.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        Provider<ApiService>(
          create: (_) => ApiService(),
        ),
        ChangeNotifierProvider<AuthService>(
          create: (context) => AuthService(context.read<ApiService>()),
        ),
        ChangeNotifierProvider<JobService>(
          create: (context) => JobService(context.read<ApiService>()),
        ),
        ChangeNotifierProvider<CustomerService>(
          create: (context) => CustomerService(context.read<ApiService>()),
        ),
        ChangeNotifierProvider<PhotoService>(
          create: (context) => PhotoService(context.read<ApiService>()),
        ),
        ChangeNotifierProvider<LocationService>(
          create: (_) => LocationService(),
        ),
        ChangeNotifierProvider<NotificationService>(
          create: (context) => NotificationService(context.read<ApiService>()),
        ),
        FutureProvider<OfflineService>(
          create: (_) async {
            final prefs = await SharedPreferences.getInstance();
            return OfflineService(prefs);
          },
          initialData: null,
        ),
      ],
      child: MaterialApp(
        title: 'Maids of Cyfair - Cleaner',
        theme: AppTheme.lightTheme,
        debugShowCheckedModeBanner: false,
        initialRoute: '/',
        routes: {
          '/': (context) => const SplashScreen(),
          '/login': (context) => const LoginScreen(),
          '/home': (context) => const HomeScreen(),
          '/job-detail': (context) => const JobDetailScreen(),
        },
      ),
    );
  }
}