class Cleaner {
  final String id;
  final String name;
  final String email;
  final String phone;
  final String? profileImage;
  final double rating;
  final int completedJobs;
  final bool isActive;
  final DateTime createdAt;

  Cleaner({
    required this.id,
    required this.name,
    required this.email,
    required this.phone,
    this.profileImage,
    this.rating = 0.0,
    this.completedJobs = 0,
    this.isActive = true,
    required this.createdAt,
  });

  factory Cleaner.fromJson(Map<String, dynamic> json) {
    return Cleaner(
      id: json['_id'] ?? json['id'] ?? '',
      name: json['name'] ?? '',
      email: json['email'] ?? '',
      phone: json['phone'] ?? '',
      profileImage: json['profileImage'],
      rating: (json['rating'] ?? 0.0).toDouble(),
      completedJobs: json['completedJobs'] ?? 0,
      isActive: json['isActive'] ?? true,
      createdAt: json['createdAt'] != null
          ? DateTime.parse(json['createdAt'])
          : DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'email': email,
      'phone': phone,
      'profileImage': profileImage,
      'rating': rating,
      'completedJobs': completedJobs,
      'isActive': isActive,
      'createdAt': createdAt.toIso8601String(),
    };
  }
}

