import 'package:flutter/foundation.dart';
import '../models/job.dart';
import '../models/message.dart';
import '../services/api_service.dart';
import '../services/location_service.dart';
import '../config/api_config.dart';

class JobProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();
  final LocationService _locationService = LocationService();

  List<Job> _jobs = [];
  Job? _currentJob;
  bool _isLoading = false;
  String? _errorMessage;

  List<Job> get jobs => _jobs;
  Job? get currentJob => _currentJob;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  List<Job> get todayJobs {
    final today = DateTime.now();
    return _jobs.where((job) {
      return job.scheduledDate.year == today.year &&
          job.scheduledDate.month == today.month &&
          job.scheduledDate.day == today.day;
    }).toList();
  }

  List<Job> get upcomingJobs {
    final today = DateTime.now();
    return _jobs.where((job) => job.scheduledDate.isAfter(today)).toList();
  }

  List<Job> get completedJobs {
    return _jobs.where((job) => job.status == JobStatus.completed).toList();
  }

  Future<void> fetchJobs() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final response = await _apiService.get(ApiConfig.jobsEndpoint);
      if (response['jobs'] != null) {
        _jobs = (response['jobs'] as List)
            .map((job) => Job.fromJson(job))
            .toList();
      }
    } catch (e) {
      // Silently fail in demo mode - use empty list
      _errorMessage = null;
      _jobs = [];
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> clockIn(String jobId) async {
    try {
      final position = await _locationService.getCurrentLocation();
      if (position == null) {
        throw Exception('Could not get location');
      }

      final response = await _apiService.post(
        ApiConfig.clockInEndpoint,
        {
          'jobId': jobId,
          'latitude': position.latitude,
          'longitude': position.longitude,
        },
      );

      if (response['job'] != null) {
        final updatedJob = Job.fromJson(response['job']);
        _updateJobInList(updatedJob);
        _currentJob = updatedJob;
        notifyListeners();
        return true;
      }
      return false;
    } catch (e) {
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      notifyListeners();
      return false;
    }
  }

  Future<bool> clockOut(String jobId) async {
    try {
      final position = await _locationService.getCurrentLocation();
      if (position == null) {
        throw Exception('Could not get location');
      }

      final response = await _apiService.post(
        ApiConfig.clockOutEndpoint,
        {
          'jobId': jobId,
          'latitude': position.latitude,
          'longitude': position.longitude,
        },
      );

      if (response['job'] != null) {
        final updatedJob = Job.fromJson(response['job']);
        _updateJobInList(updatedJob);
        if (_currentJob?.id == jobId) {
          _currentJob = null;
        }
        notifyListeners();
        return true;
      }
      return false;
    } catch (e) {
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      notifyListeners();
      return false;
    }
  }

  Future<bool> updateETA(String jobId, String eta) async {
    try {
      final response = await _apiService.post(
        ApiConfig.updateEtaEndpoint,
        {
          'jobId': jobId,
          'eta': eta,
        },
      );

      if (response['job'] != null) {
        final updatedJob = Job.fromJson(response['job']);
        _updateJobInList(updatedJob);
        notifyListeners();
        return true;
      }
      return false;
    } catch (e) {
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      notifyListeners();
      return false;
    }
  }

  Future<bool> sendMessage(String jobId, String message) async {
    try {
      await _apiService.post(
        ApiConfig.sendMessageEndpoint,
        {
          'jobId': jobId,
          'message': message,
        },
      );
      return true;
    } catch (e) {
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      notifyListeners();
      return false;
    }
  }

  Future<bool> updateTaskStatus(String jobId, String taskId, bool isCompleted) async {
    try {
      final job = _jobs.firstWhere((j) => j.id == jobId);
      final updatedTasks = job.tasks.map((task) {
        if (task.id == taskId) {
          return task.copyWith(isCompleted: isCompleted);
        }
        return task;
      }).toList();

      final updatedJob = job.copyWith(tasks: updatedTasks);
      _updateJobInList(updatedJob);
      notifyListeners();
      return true;
    } catch (e) {
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      notifyListeners();
      return false;
    }
  }

  void setCurrentJob(Job? job) {
    _currentJob = job;
    notifyListeners();
  }

  void _updateJobInList(Job updatedJob) {
    final index = _jobs.indexWhere((j) => j.id == updatedJob.id);
    if (index != -1) {
      _jobs[index] = updatedJob;
    }
  }

  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }
}

