import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import '../models/job.dart';
import '../models/cleaner.dart';
import '../models/customer.dart';

class OfflineService extends ChangeNotifier {
  final SharedPreferences _prefs;
  final Connectivity _connectivity = Connectivity();
  
  bool _isOnline = true;
  List<JobModel> _offlineJobs = [];
  List<Map<String, dynamic>> _pendingUpdates = [];
  
  OfflineService(this._prefs) {
    _initializeConnectivity();
    _loadOfflineData();
  }
  
  // Getters
  bool get isOnline => _isOnline;
  List<JobModel> get offlineJobs => _offlineJobs;
  List<Map<String, dynamic>> get pendingUpdates => _pendingUpdates;
  
  // Initialize connectivity monitoring
  void _initializeConnectivity() {
    _connectivity.onConnectivityChanged.listen((ConnectivityResult result) {
      _isOnline = result != ConnectivityResult.none;
      notifyListeners();
      
      if (_isOnline) {
        _syncPendingUpdates();
      }
    });
  }
  
  // Load offline data
  void _loadOfflineData() {
    _loadOfflineJobs();
    _loadPendingUpdates();
  }
  
  // Save job offline
  Future<void> saveJobOffline(JobModel job) async {
    try {
      _offlineJobs.removeWhere((j) => j.id == job.id);
      _offlineJobs.add(job);
      
      final jobsJson = _offlineJobs.map((j) => j.toJson()).toList();
      await _prefs.setString('offline_jobs', jsonEncode(jobsJson));
      
      notifyListeners();
    } catch (e) {
      print('Failed to save job offline: ${e.toString()}');
    }
  }
  
  // Load offline jobs
  void _loadOfflineJobs() {
    try {
      final jobsJson = _prefs.getString('offline_jobs');
      if (jobsJson != null) {
        final List<dynamic> jobsList = jsonDecode(jobsJson);
            _offlineJobs = jobsList.map((json) => JobModel.fromJson(json)).toList();
      }
    } catch (e) {
      print('Failed to load offline jobs: ${e.toString()}');
    }
  }
  
  // Save pending update
  Future<void> savePendingUpdate(String type, String jobId, Map<String, dynamic> data) async {
    try {
      final update = {
        'id': DateTime.now().millisecondsSinceEpoch.toString(),
        'type': type,
        'job_id': jobId,
        'data': data,
        'timestamp': DateTime.now().toIso8601String(),
      };
      
      _pendingUpdates.add(update);
      
      await _prefs.setString('pending_updates', jsonEncode(_pendingUpdates));
      notifyListeners();
    } catch (e) {
      print('Failed to save pending update: ${e.toString()}');
    }
  }
  
  // Load pending updates
  void _loadPendingUpdates() {
    try {
      final updatesJson = _prefs.getString('pending_updates');
      if (updatesJson != null) {
        final List<dynamic> updatesList = jsonDecode(updatesJson);
        _pendingUpdates = updatesList.cast<Map<String, dynamic>>();
      }
    } catch (e) {
      print('Failed to load pending updates: ${e.toString()}');
    }
  }
  
  // Sync pending updates when online
  Future<void> _syncPendingUpdates() async {
    if (_pendingUpdates.isEmpty) return;
    
    // In a real implementation, you would send these updates to the server
    // For now, we'll just clear them after a delay
    await Future.delayed(const Duration(seconds: 2));
    
    _pendingUpdates.clear();
    await _prefs.remove('pending_updates');
    notifyListeners();
  }
  
  // Get job by ID (check offline first, then online)
  JobModel? getJobById(String jobId) {
    try {
      return _offlineJobs.firstWhere((job) => job.id == jobId);
    } catch (e) {
      return null;
    }
  }
  
  // Update job status offline
  Future<void> updateJobStatusOffline(String jobId, String status) async {
    final jobIndex = _offlineJobs.indexWhere((job) => job.id == jobId);
    if (jobIndex != -1) {
          final updatedJob = JobModel.fromJson({
        ..._offlineJobs[jobIndex].toJson(),
        'status': status,
        'updated_at': DateTime.now().toIso8601String(),
      });
      _offlineJobs[jobIndex] = updatedJob;
      
      await saveJobOffline(updatedJob);
      await savePendingUpdate('status_update', jobId, {'status': status});
    }
  }
  
  // Update job progress offline
  Future<void> updateJobProgressOffline(String jobId, Map<String, dynamic> progressData) async {
    final jobIndex = _offlineJobs.indexWhere((job) => job.id == jobId);
    if (jobIndex != -1) {
          final updatedJob = JobModel.fromJson({
        ..._offlineJobs[jobIndex].toJson(),
        'progress': progressData,
        'updated_at': DateTime.now().toIso8601String(),
      });
      _offlineJobs[jobIndex] = updatedJob;
      
      await saveJobOffline(updatedJob);
      await savePendingUpdate('progress_update', jobId, progressData);
    }
  }
  
  // Update job checklist offline
  Future<void> updateJobChecklistOffline(String jobId, List<Map<String, dynamic>> checklist) async {
    final jobIndex = _offlineJobs.indexWhere((job) => job.id == jobId);
    if (jobIndex != -1) {
          final updatedJob = JobModel.fromJson({
        ..._offlineJobs[jobIndex].toJson(),
        'checklist': checklist,
        'updated_at': DateTime.now().toIso8601String(),
      });
      _offlineJobs[jobIndex] = updatedJob;
      
      await saveJobOffline(updatedJob);
      await savePendingUpdate('checklist_update', jobId, {'checklist': checklist});
    }
  }
  
  // Update job ETA offline
  Future<void> updateJobETAOffline(String jobId, String eta) async {
    final jobIndex = _offlineJobs.indexWhere((job) => job.id == jobId);
    if (jobIndex != -1) {
          final updatedJob = JobModel.fromJson({
        ..._offlineJobs[jobIndex].toJson(),
        'eta': eta,
        'updated_at': DateTime.now().toIso8601String(),
      });
      _offlineJobs[jobIndex] = updatedJob;
      
      await saveJobOffline(updatedJob);
      await savePendingUpdate('eta_update', jobId, {'eta': eta});
    }
  }
  
  // Clear offline data
  Future<void> clearOfflineData() async {
    _offlineJobs.clear();
    _pendingUpdates.clear();
    
    await _prefs.remove('offline_jobs');
    await _prefs.remove('pending_updates');
    
    notifyListeners();
  }
  
  // Check if job has pending updates
  bool hasPendingUpdates(String jobId) {
    return _pendingUpdates.any((update) => update['job_id'] == jobId);
  }
  
  // Get pending updates for job
  List<Map<String, dynamic>> getPendingUpdatesForJob(String jobId) {
    return _pendingUpdates.where((update) => update['job_id'] == jobId).toList();
  }
}
