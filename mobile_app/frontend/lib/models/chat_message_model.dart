class ChatMessageModel {
  final String id;
  final String content;
  final bool isUser;
  final DateTime timestamp;
  final List<SourceReference> sources;
  final bool isLoading;

  const ChatMessageModel({
    required this.id,
    required this.content,
    required this.isUser,
    required this.timestamp,
    this.sources = const [],
    this.isLoading = false,
  });

  factory ChatMessageModel.fromJson(Map<String, dynamic> json) {
    return ChatMessageModel(
      id: json['id'] ?? json['_id'] ?? DateTime.now().millisecondsSinceEpoch.toString(),
      content: json['content'] ?? '',
      isUser: json['role'] == 'user',
      timestamp: json['createdAt'] != null
          ? DateTime.tryParse(json['createdAt']) ?? DateTime.now()
          : DateTime.now(),
      sources: json['sources'] != null
          ? (json['sources'] as List)
              .map((s) => SourceReference.fromJson(s as Map<String, dynamic>))
              .toList()
          : const [],
    );
  }
}

class SourceReference {
  final String documentId;
  final String documentName;
  final String excerpt;
  final int? pageNumber;
  final String? viewUrl;

  const SourceReference({
    required this.documentId,
    required this.documentName,
    required this.excerpt,
    this.pageNumber,
    this.viewUrl,
  });

  factory SourceReference.fromJson(Map<String, dynamic> json) {
    return SourceReference(
      documentId: json['documentId'] ?? '',
      documentName: json['documentName'] ?? 'Unknown',
      excerpt: json['excerpt'] ?? '',
      pageNumber: json['pageNumber'],
      viewUrl: json['viewUrl'],
    );
  }
}
