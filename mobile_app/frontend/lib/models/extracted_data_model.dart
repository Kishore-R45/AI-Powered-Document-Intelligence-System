class ExtractedDataModel {
  final String id;
  final String documentId;
  final String documentName;
  final String documentType;
  final String category;
  final Map<String, String> data;
  final DateTime extractedAt;
  final bool isSynced;
  final String processingStatus;

  const ExtractedDataModel({
    required this.id,
    required this.documentId,
    required this.documentName,
    required this.documentType,
    required this.category,
    required this.data,
    required this.extractedAt,
    this.isSynced = true,
    this.processingStatus = 'completed',
  });

  /// Parse from backend GET /documents/<id>/extracted-data response.
  /// The backend returns: { document: {...}, extracted_data: {...}, processing_status: ... }
  factory ExtractedDataModel.fromJson(Map<String, dynamic> json) {
    // Handle both flat format and nested backend format
    final rawData = json['extracted_data'] ?? json['data'] ?? {};
    final Map<String, String> parsed = {};
    if (rawData is Map) {
      for (final entry in rawData.entries) {
        if (entry.value != null && entry.value.toString().isNotEmpty) {
          parsed[entry.key.toString()] = entry.value.toString();
        }
      }
    }

    // Backend nests document info inside 'document' key
    final doc = json['document'] as Map<String, dynamic>? ?? json;

    return ExtractedDataModel(
      id: json['id'] ?? doc['id'] ?? '',
      documentId: json['documentId'] ?? doc['id'] ?? '',
      documentName: json['documentName'] ?? doc['name'] ?? '',
      documentType: json['documentType'] ?? doc['type'] ?? json['type'] ?? '',
      category: json['category'] ?? doc['category'] ?? 'Other',
      data: parsed,
      extractedAt: json['extractedAt'] != null
          ? (DateTime.tryParse(json['extractedAt'])?.toLocal() ?? DateTime.now())
          : DateTime.now(),
      isSynced: json['isSynced'] ?? true,
      processingStatus: json['processing_status'] ?? json['processingStatus'] ?? 'completed',
    );
  }

  /// Build from a DocumentModel that already has extractedData populated.
  factory ExtractedDataModel.fromDocument(dynamic doc) {
    final Map<String, String> parsed = {};
    if (doc.extractedData is Map) {
      for (final entry in (doc.extractedData as Map).entries) {
        if (entry.value != null && entry.value.toString().isNotEmpty) {
          parsed[entry.key.toString()] = entry.value.toString();
        }
      }
    }
    return ExtractedDataModel(
      id: doc.id,
      documentId: doc.id,
      documentName: doc.name,
      documentType: doc.type,
      category: doc.category,
      data: parsed,
      extractedAt: doc.uploadDate,
      processingStatus: doc.processingStatus ?? 'completed',
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
    String? processingStatus,
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
      processingStatus: processingStatus ?? this.processingStatus,
    );
  }
}
