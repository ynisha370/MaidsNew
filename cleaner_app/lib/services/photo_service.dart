import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart' as path;
import 'api_service.dart';

class PhotoService extends ChangeNotifier {
  final ApiService _apiService;
  final ImagePicker _imagePicker = ImagePicker();
  
  List<String> _jobPhotos = [];
  bool _isUploading = false;
  String? _errorMessage;
  
  PhotoService(this._apiService);
  
  // Getters
  List<String> get jobPhotos => _jobPhotos;
  bool get isUploading => _isUploading;
  String? get errorMessage => _errorMessage;
  
  // Take photo from camera
  Future<String?> takePhoto() async {
    try {
      final XFile? image = await _imagePicker.pickImage(
        source: ImageSource.camera,
        imageQuality: 85,
        maxWidth: 1920,
        maxHeight: 1080,
      );
      
      if (image != null) {
        // Save to app directory
        final appDir = await getApplicationDocumentsDirectory();
        final fileName = 'job_photo_${DateTime.now().millisecondsSinceEpoch}.jpg';
        final filePath = path.join(appDir.path, 'photos', fileName);
        
        // Create photos directory if it doesn't exist
        final photosDir = Directory(path.dirname(filePath));
        if (!await photosDir.exists()) {
          await photosDir.create(recursive: true);
        }
        
        // Copy image to app directory
        final File savedImage = await File(image.path).copy(filePath);
        return savedImage.path;
      }
      
      return null;
    } catch (e) {
      _setError('Failed to take photo: ${e.toString()}');
      return null;
    }
  }
  
  // Pick photo from gallery
  Future<String?> pickPhotoFromGallery() async {
    try {
      final XFile? image = await _imagePicker.pickImage(
        source: ImageSource.gallery,
        imageQuality: 85,
        maxWidth: 1920,
        maxHeight: 1080,
      );
      
      if (image != null) {
        // Save to app directory
        final appDir = await getApplicationDocumentsDirectory();
        final fileName = 'job_photo_${DateTime.now().millisecondsSinceEpoch}.jpg';
        final filePath = path.join(appDir.path, 'photos', fileName);
        
        // Create photos directory if it doesn't exist
        final photosDir = Directory(path.dirname(filePath));
        if (!await photosDir.exists()) {
          await photosDir.create(recursive: true);
        }
        
        // Copy image to app directory
        final File savedImage = await File(image.path).copy(filePath);
        return savedImage.path;
      }
      
      return null;
    } catch (e) {
      _setError('Failed to pick photo: ${e.toString()}');
      return null;
    }
  }
  
  // Add photo to job
  void addPhotoToJob(String photoPath) {
    if (!_jobPhotos.contains(photoPath)) {
      _jobPhotos.add(photoPath);
      notifyListeners();
    }
  }
  
  // Remove photo from job
  void removePhotoFromJob(String photoPath) {
    _jobPhotos.remove(photoPath);
    notifyListeners();
  }
  
  // Clear all photos
  void clearPhotos() {
    _jobPhotos.clear();
    notifyListeners();
  }
  
  // Upload photos to server
  Future<bool> uploadPhotos(String jobId) async {
    if (_jobPhotos.isEmpty) return true;
    
    _setUploading(true);
    _clearError();
    
    try {
      final result = await _apiService.uploadJobPhotos(jobId, _jobPhotos);
      
      if (result['success']) {
        _clearError();
        return true;
      } else {
        _setError(result['error']);
        return false;
      }
    } catch (e) {
      _setError('Failed to upload photos: ${e.toString()}');
      return false;
    } finally {
      _setUploading(false);
    }
  }
  
  // Load photos for job
  Future<void> loadJobPhotos(String jobId) async {
    _setUploading(true);
    _clearError();
    
    try {
      final result = await _apiService.getJobPhotos(jobId);
      
      if (result['success']) {
        final photos = result['data']['photos'] as List<dynamic>?;
        _jobPhotos = photos?.cast<String>() ?? [];
        notifyListeners();
      } else {
        _setError(result['error']);
      }
    } catch (e) {
      _setError('Failed to load photos: ${e.toString()}');
    } finally {
      _setUploading(false);
    }
  }
  
  // Delete local photo file
  Future<void> deleteLocalPhoto(String photoPath) async {
    try {
      final file = File(photoPath);
      if (await file.exists()) {
        await file.delete();
      }
    } catch (e) {
      _setError('Failed to delete photo: ${e.toString()}');
    }
  }
  
  // Helper methods
  void _setUploading(bool uploading) {
    _isUploading = uploading;
    notifyListeners();
  }
  
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
