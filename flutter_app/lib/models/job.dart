class Job {
  final String id;
  final String clientName;
  final String clientPhone;
  final String clientAddress;
  final String serviceType;
  final DateTime scheduledDate;
  final String scheduledTime;
  final double price;
  final JobStatus status;
  final List<Task> tasks;
  final String? notes;
  final String? eta;
  final DateTime? clockInTime;
  final DateTime? clockOutTime;
  final String? assignedCleanerId;

  Job({
    required this.id,
    required this.clientName,
    required this.clientPhone,
    required this.clientAddress,
    required this.serviceType,
    required this.scheduledDate,
    required this.scheduledTime,
    required this.price,
    this.status = JobStatus.pending,
    this.tasks = const [],
    this.notes,
    this.eta,
    this.clockInTime,
    this.clockOutTime,
    this.assignedCleanerId,
  });

  factory Job.fromJson(Map<String, dynamic> json) {
    return Job(
      id: json['_id'] ?? json['id'] ?? '',
      clientName: json['clientName'] ?? '',
      clientPhone: json['clientPhone'] ?? '',
      clientAddress: json['clientAddress'] ?? '',
      serviceType: json['serviceType'] ?? '',
      scheduledDate: json['scheduledDate'] != null
          ? DateTime.parse(json['scheduledDate'])
          : DateTime.now(),
      scheduledTime: json['scheduledTime'] ?? '',
      price: (json['price'] ?? 0.0).toDouble(),
      status: JobStatus.values.firstWhere(
        (e) => e.toString() == 'JobStatus.${json['status']}',
        orElse: () => JobStatus.pending,
      ),
      tasks: json['tasks'] != null
          ? (json['tasks'] as List).map((t) => Task.fromJson(t)).toList()
          : [],
      notes: json['notes'],
      eta: json['eta'],
      clockInTime: json['clockInTime'] != null
          ? DateTime.parse(json['clockInTime'])
          : null,
      clockOutTime: json['clockOutTime'] != null
          ? DateTime.parse(json['clockOutTime'])
          : null,
      assignedCleanerId: json['assignedCleanerId'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'clientName': clientName,
      'clientPhone': clientPhone,
      'clientAddress': clientAddress,
      'serviceType': serviceType,
      'scheduledDate': scheduledDate.toIso8601String(),
      'scheduledTime': scheduledTime,
      'price': price,
      'status': status.toString().split('.').last,
      'tasks': tasks.map((t) => t.toJson()).toList(),
      'notes': notes,
      'eta': eta,
      'clockInTime': clockInTime?.toIso8601String(),
      'clockOutTime': clockOutTime?.toIso8601String(),
      'assignedCleanerId': assignedCleanerId,
    };
  }

  Job copyWith({
    String? id,
    String? clientName,
    String? clientPhone,
    String? clientAddress,
    String? serviceType,
    DateTime? scheduledDate,
    String? scheduledTime,
    double? price,
    JobStatus? status,
    List<Task>? tasks,
    String? notes,
    String? eta,
    DateTime? clockInTime,
    DateTime? clockOutTime,
    String? assignedCleanerId,
  }) {
    return Job(
      id: id ?? this.id,
      clientName: clientName ?? this.clientName,
      clientPhone: clientPhone ?? this.clientPhone,
      clientAddress: clientAddress ?? this.clientAddress,
      serviceType: serviceType ?? this.serviceType,
      scheduledDate: scheduledDate ?? this.scheduledDate,
      scheduledTime: scheduledTime ?? this.scheduledTime,
      price: price ?? this.price,
      status: status ?? this.status,
      tasks: tasks ?? this.tasks,
      notes: notes ?? this.notes,
      eta: eta ?? this.eta,
      clockInTime: clockInTime ?? this.clockInTime,
      clockOutTime: clockOutTime ?? this.clockOutTime,
      assignedCleanerId: assignedCleanerId ?? this.assignedCleanerId,
    );
  }
}

enum JobStatus {
  pending,
  assigned,
  inProgress,
  completed,
  cancelled,
}

class Task {
  final String id;
  final String description;
  final bool isCompleted;

  Task({
    required this.id,
    required this.description,
    this.isCompleted = false,
  });

  factory Task.fromJson(Map<String, dynamic> json) {
    return Task(
      id: json['id'] ?? '',
      description: json['description'] ?? '',
      isCompleted: json['isCompleted'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'description': description,
      'isCompleted': isCompleted,
    };
  }

  Task copyWith({
    String? id,
    String? description,
    bool? isCompleted,
  }) {
    return Task(
      id: id ?? this.id,
      description: description ?? this.description,
      isCompleted: isCompleted ?? this.isCompleted,
    );
  }
}

