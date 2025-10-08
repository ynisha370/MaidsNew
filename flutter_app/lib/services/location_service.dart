import 'package:geolocator/geolocator.dart';
import 'package:permission_handler/permission_handler.dart';

class LocationService {
  Future<bool> requestLocationPermission() async {
    final status = await Permission.location.request();
    return status.isGranted;
  }

  Future<Position?> getCurrentLocation() async {
    try {
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        throw Exception('Location services are disabled.');
      }

      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          throw Exception('Location permissions are denied');
        }
      }

      if (permission == LocationPermission.deniedForever) {
        throw Exception('Location permissions are permanently denied');
      }

      return await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
      );
    } catch (e) {
      print('Error getting location: $e');
      return null;
    }
  }

  Future<double> getDistanceInMeters(
    double startLat,
    double startLng,
    double endLat,
    double endLng,
  ) async {
    return Geolocator.distanceBetween(startLat, startLng, endLat, endLng);
  }

  Future<String> calculateETA(
    double distanceInMeters,
    double averageSpeedKmh,
  ) async {
    final distanceInKm = distanceInMeters / 1000;
    final timeInHours = distanceInKm / averageSpeedKmh;
    final timeInMinutes = (timeInHours * 60).round();

    if (timeInMinutes < 60) {
      return '$timeInMinutes minutes';
    } else {
      final hours = timeInMinutes ~/ 60;
      final minutes = timeInMinutes % 60;
      return '$hours hour${hours > 1 ? 's' : ''} $minutes min';
    }
  }
}

