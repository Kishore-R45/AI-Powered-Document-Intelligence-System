class ExtractedDataModel {
  final String id;
  final String documentId;
  final String documentName;
  final String documentType;
  final String category;
  final Map<String, String> data;
  final DateTime extractedAt;
  final bool isSynced;

  const ExtractedDataModel({
    required this.id,
    required this.documentId,
    required this.documentName,
    required this.documentType,
    required this.category,
    required this.data,
    required this.extractedAt,
    this.isSynced = true,
  });

  factory ExtractedDataModel.fromJson(Map<String, dynamic> json) {
    return ExtractedDataModel(
      id: json['id'] ?? '',
      documentId: json['documentId'] ?? '',
      documentName: json['documentName'] ?? '',
      documentType: json['documentType'] ?? json['type'] ?? '',
      category: json['category'] ?? 'Other',
      data: json['data'] != null
          ? Map<String, String>.from(
              (json['data'] as Map).map((k, v) => MapEntry(k.toString(), v.toString())))
          : {},
      extractedAt: json['extractedAt'] != null
          ? DateTime.tryParse(json['extractedAt']) ?? DateTime.now()
          : DateTime.now(),
      isSynced: json['isSynced'] ?? true,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'documentId': documentId,
        'documentName': documentName,
        'documentType': documentType,
        'category': category,
        'data': data,
        'extractedAt': extractedAt.toIso8601String(),
        'isSynced': isSynced,
      };

  int get fieldCount => data.length;

  ExtractedDataModel copyWith({
    String? id,
    String? documentId,
    String? documentName,
    String? documentType,
    String? category,
    Map<String, String>? data,
    DateTime? extractedAt,
    bool? isSynced,
  }) {
    return ExtractedDataModel(
      id: id ?? this.id,
      documentId: documentId ?? this.documentId,
      documentName: documentName ?? this.documentName,
      documentType: documentType ?? this.documentType,
      category: category ?? this.category,
      data: data ?? this.data,
      extractedAt: extractedAt ?? this.extractedAt,
      isSynced: isSynced ?? this.isSynced,
    );
  }
}
