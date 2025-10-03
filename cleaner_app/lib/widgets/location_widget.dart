import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/location_service.dart';
import '../utils/app_theme.dart';

class LocationWidget extends StatelessWidget {
  final String address;
  final double? latitude;
  final double? longitude;
  
  const LocationWidget({
    super.key,
    required this.address,
    this.latitude,
    this.longitude,
  });

  @override
  Widget build(BuildContext context) {
    return Consumer<LocationService>(
      builder: (context, locationService, child) {
        return Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Icon(
                      Icons.location_on,
                      color: AppTheme.primaryColor,
                      size: 20,
                    ),
                    const SizedBox(width: 8),
                    const Text(
                      'Job Location',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const Spacer(),
                    if (locationService.currentPosition != null)
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 8,
                          vertical: 4,
                        ),
                        decoration: BoxDecoration(
                          color: AppTheme.successColor.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: const Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(
                              Icons.my_location,
                              size: 12,
                              color: AppTheme.successColor,
                            ),
                            SizedBox(width: 4),
                            Text(
                              'GPS',
                              style: TextStyle(
                                fontSize: 10,
                                color: AppTheme.successColor,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ],
                        ),
                      ),
                  ],
                ),
                
                const SizedBox(height: 12),
                
                Text(
                  address,
                  style: const TextStyle(
                    fontSize: 14,
                    color: AppTheme.gray700,
                  ),
                ),
                
                const SizedBox(height: 16),
                
                Row(
                  children: [
                    Expanded(
                      child: ElevatedButton.icon(
                        onPressed: () => _navigateToLocation(locationService),
                        icon: const Icon(Icons.directions, size: 18),
                        label: const Text('Navigate'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: AppTheme.primaryColor,
                          foregroundColor: Colors.white,
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    OutlinedButton.icon(
                      onPressed: () => _getCurrentLocation(locationService),
                      icon: const Icon(Icons.my_location, size: 18),
                      label: const Text('My Location'),
                    ),
                  ],
                ),
                
                if (locationService.currentPosition != null) ...[
                  const SizedBox(height: 12),
                  _buildDistanceInfo(locationService),
                ],
              ],
            ),
          ),
        );
      },
    );
  }
  
  Widget _buildDistanceInfo(LocationService locationService) {
    if (latitude == null || longitude == null) {
      return const SizedBox.shrink();
    }
    
    final distance = locationService.calculateDistance(
      locationService.currentPosition!.latitude,
      locationService.currentPosition!.longitude,
      latitude!,
      longitude!,
    );
    
    final distanceText = distance < 1000 
        ? '${distance.round()}m away'
        : '${(distance / 1000).toStringAsFixed(1)}km away';
    
    final isAtLocation = locationService.isAtJobLocation(latitude!, longitude!);
    
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: isAtLocation 
            ? AppTheme.successColor.withOpacity(0.1)
            : AppTheme.warningColor.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          Icon(
            isAtLocation ? Icons.check_circle : Icons.location_searching,
            size: 16,
            color: isAtLocation ? AppTheme.successColor : AppTheme.warningColor,
          ),
          const SizedBox(width: 8),
          Text(
            isAtLocation ? 'You are at the job location' : distanceText,
            style: TextStyle(
              fontSize: 12,
              color: isAtLocation ? AppTheme.successColor : AppTheme.warningColor,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }
  
  void _navigateToLocation(LocationService locationService) {
    if (latitude != null && longitude != null) {
      locationService.navigateToCoordinates(latitude!, longitude!);
    } else {
      locationService.navigateToAddress(address);
    }
  }
  
  void _getCurrentLocation(LocationService locationService) {
    locationService.getCurrentLocation();
  }
}
