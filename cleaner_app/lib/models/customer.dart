class Customer {
  // Servicable zip codes
  static const List<String> servicableZipCodes = ['77433', '77429', '77095', '77377', '77070', '77065'];
  
  final String id;
  final String email;
  final String firstName;
  final String lastName;
  final String phone;
  final String? address;
  final String? city;
  final String? state;
  final String? zipCode;
  final bool isGuest;
  final DateTime createdAt;
  
  Customer({
    required this.id,
    required this.email,
    required this.firstName,
    required this.lastName,
    required this.phone,
    this.address,
    this.city,
    this.state,
    this.zipCode,
    this.isGuest = false,
    required this.createdAt,
  });
  
  factory Customer.fromJson(Map<String, dynamic> json) {
    return Customer(
      id: json['id'],
      email: json['email'],
      firstName: json['first_name'],
      lastName: json['last_name'],
      phone: json['phone'] ?? '',
      address: json['address'],
      city: json['city'],
      state: json['state'],
      zipCode: json['zip_code'],
      isGuest: json['is_guest'] ?? false,
      createdAt: DateTime.parse(json['created_at']),
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'first_name': firstName,
      'last_name': lastName,
      'phone': phone,
      'address': address,
      'city': city,
      'state': state,
      'zip_code': zipCode,
      'is_guest': isGuest,
      'created_at': createdAt.toIso8601String(),
    };
  }
  
  String get fullName => '$firstName $lastName';
  
  String get displayName => fullName;
  
  String get fullAddress {
    final parts = <String>[];
    if (address != null && address!.isNotEmpty) parts.add(address!);
    if (city != null && city!.isNotEmpty) parts.add(city!);
    if (state != null && state!.isNotEmpty) parts.add(state!);
    if (zipCode != null && zipCode!.isNotEmpty) parts.add(zipCode!);
    return parts.join(', ');
  }
  
  bool get hasCompleteAddress => 
      address != null && address!.isNotEmpty &&
      city != null && city!.isNotEmpty &&
      state != null && state!.isNotEmpty &&
      zipCode != null && zipCode!.isNotEmpty;
  
  /// Validates if the zip code is in the servicable area
  static bool isValidZipCode(String? zipCode) {
    if (zipCode == null || zipCode.isEmpty) return false;
    return servicableZipCodes.contains(zipCode);
  }
  
  /// Validates if the current customer's zip code is servicable
  bool get hasValidZipCode => isValidZipCode(zipCode);
  
  /// Gets validation error message for zip code
  static String? getZipCodeValidationError(String? zipCode) {
    if (zipCode == null || zipCode.isEmpty) {
      return 'ZIP code is required';
    }
    if (!isValidZipCode(zipCode)) {
      return 'We currently only service these ZIP codes: ${servicableZipCodes.join(', ')}';
    }
    return null;
  }
}