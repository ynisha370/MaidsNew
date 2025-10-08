class Message {
  final String id;
  final String jobId;
  final String senderId;
  final String senderName;
  final String receiverId;
  final String content;
  final MessageType type;
  final DateTime timestamp;
  final bool isRead;

  Message({
    required this.id,
    required this.jobId,
    required this.senderId,
    required this.senderName,
    required this.receiverId,
    required this.content,
    this.type = MessageType.text,
    required this.timestamp,
    this.isRead = false,
  });

  factory Message.fromJson(Map<String, dynamic> json) {
    return Message(
      id: json['_id'] ?? json['id'] ?? '',
      jobId: json['jobId'] ?? '',
      senderId: json['senderId'] ?? '',
      senderName: json['senderName'] ?? '',
      receiverId: json['receiverId'] ?? '',
      content: json['content'] ?? '',
      type: MessageType.values.firstWhere(
        (e) => e.toString() == 'MessageType.${json['type']}',
        orElse: () => MessageType.text,
      ),
      timestamp: json['timestamp'] != null
          ? DateTime.parse(json['timestamp'])
          : DateTime.now(),
      isRead: json['isRead'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'jobId': jobId,
      'senderId': senderId,
      'senderName': senderName,
      'receiverId': receiverId,
      'content': content,
      'type': type.toString().split('.').last,
      'timestamp': timestamp.toIso8601String(),
      'isRead': isRead,
    };
  }
}

enum MessageType {
  text,
  eta,
  image,
  system,
}

