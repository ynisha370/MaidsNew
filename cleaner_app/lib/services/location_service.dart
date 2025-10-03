import 'dart:async';
import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:url_launcher/url_launcher.dart';

class LocationService extends ChangeNotifier {
  Position? _currentPosition;
  bool _isTracking = false;
  bool _hasPermission = false;
  String? _errorMessage;
  StreamSubscription<Position>? _positionStream;
  
  LocationService() {
    _checkPermission();
  }
  
  // Getters
  Position? get currentPosition => _currentPosition;
  bool get isTracking => _isTracking;
  bool get hasPermission => _hasPermission;
  String? get errorMessage => _errorMessage;
  
  // Check location permission
  Future<bool> _checkPermission() async {
    final permission = await Permission.location.status;
    _hasPermission = permission.isGranted;
    notifyListeners();
    return _hasPermission;
  }
  
  // Request location permission
  Future<bool> requestPermission() async {
    final permission = await Permission.location.request();
    _hasPermission = permission.isGranted;
    notifyListeners();
    return _hasPermission;
  }
  
  // Get current location
  Future<Position?> getCurrentLocation() async {
    if (!_hasPermission) {
      final granted = await requestPermission();
      if (!granted) {
        _setError('Location permission denied');
        return null;
      }
    }
    
    try {
      _currentPosition = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
      );
      notifyListeners();
      return _currentPosition;
    } catch (e) {
      _setError('Failed to get current location: ${e.toString()}');
      return null;
    }
  }
  
  // Start location tracking
  Future<void> startTracking() async {
    if (!_hasPermission) {
      final granted = await requestPermission();
      if (!granted) {
        _setError('Location permission denied');
        return;
      }
    }
    
    try {
      _positionStream = Geolocator.getPositionStream(
        locationSettings: const LocationSettings(
          accuracy: LocationAccuracy.high,
          distanceFilter: 10, // Update every 10 meters
        ),
      ).listen(
        (Position position) {
          _currentPosition = position;
          notifyListeners();
        },
        onError: (error) {
          _setError('Location tracking error: $error');
        },
      );
      
      _isTracking = true;
      notifyListeners();
    } catch (e) {
      _setError('Failed to start location tracking: ${e.toString()}');
    }
  }
  
  // Stop location tracking
  void stopTracking() {
    _positionStream?.cancel();
    _positionStream = null;
    _isTracking = false;
    notifyListeners();
  }
  
  // Calculate distance between two points
  double calculateDistance(double lat1, double lon1, double lat2, double lon2) {
    return Geolocator.distanceBetween(lat1, lon1, lat2, lon2);
  }
  
  // Check if cleaner is at job location
  bool isAtJobLocation(double jobLat, double jobLon, {double radiusMeters = 100}) {
    if (_currentPosition == null) return false;
    
    final distance = calculateDistance(
      _currentPosition!.latitude,
      _currentPosition!.longitude,
      jobLat,
      jobLon,
    );
    
    return distance <= radiusMeters;
  }
  
  // Open navigation to address
  Future<void> navigateToAddress(String address) async {
    try {
      final encodedAddress = Uri.encodeComponent(address);
      final url = 'https://www.google.com/maps/dir/?api=1&destination=$encodedAddress';
      
      if (await canLaunchUrl(Uri.parse(url))) {
        await launchUrl(Uri.parse(url), mode: LaunchMode.externalApplication);
      } else {
        _setError('Could not open navigation app');
      }
    } catch (e) {
      _setError('Failed to open navigation: ${e.toString()}');
    }
  }
  
  // Open navigation to coordinates
  Future<void> navigateToCoordinates(double lat, double lon) async {
    try {
      final url = 'https://www.google.com/maps/dir/?api=1&destination=$lat,$lon';
      
      if (await canLaunchUrl(Uri.parse(url))) {
        await launchUrl(Uri.parse(url), mode: LaunchMode.externalApplication);
      } else {
        _setError('Could not open navigation app');
      }
    } catch (e) {
      _setError('Failed to open navigation: ${e.toString()}');
    }
  }
  
  // Get formatted address from coordinates
  Future<String?> getAddressFromCoordinates(double lat, double lon) async {
    try {
      // TODO: Fix Geolocator API - method name may have changed
      // final placemarks = await Geolocator.placemarkFromCoordinates(lat, lon);
      // if (placemarks.isNotEmpty) {
      //   final placemark = placemarks.first;
      //   return '${placemark.street}, ${placemark.locality}, ${placemark.administrativeArea} ${placemark.postalCode}';
      // }
      return 'Address lookup temporarily disabled';
    } catch (e) {
      _setError('Failed to get address: ${e.toString()}');
      return null;
    }
  }
  
  // Helper methods
  void _setError(String error) {
    _errorMessage = error;
    notifyListeners();
  }
  
  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }
  
  @override
  void dispose() {
    stopTracking();
    super.dispose();
  }
}
