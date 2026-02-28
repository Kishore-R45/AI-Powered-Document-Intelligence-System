class DocumentModel {
  final String id;
  final String name;
  final String type;
  final String category;
  final DateTime uploadDate;
  final DateTime? expiryDate;
  final String? fileUrl;
  final String? localPath;
  final String? thumbnailUrl;
  final int fileSize;
  final List<String> tags;
  final bool isOfflineAvailable;
  final String status; // 'active', 'expiring', 'expired'

  const DocumentModel({
    required this.id,
    required this.name,
    required this.type,
    required this.category,
    required this.uploadDate,
    this.expiryDate,
    this.fileUrl,
    this.localPath,
    this.thumbnailUrl,
    this.fileSize = 0,
    this.tags = const [],
    this.isOfflineAvailable = true,
    this.status = 'active',
  });

  factory DocumentModel.fromJson(Map<String, dynamic> json) {
    // Determine status from expiry
    String status = 'active';
    DateTime? expiry;
    if (json['expiryDate'] != null) {
      expiry = DateTime.tryParse(json['expiryDate']);
      if (expiry != null) {
        if (expiry.isBefore(DateTime.now())) {
          status = 'expired';
        } else if (expiry.difference(DateTime.now()).inDays <= 30) {
          status = 'expiring';
        }
      }
    }

    // Map backend 'type' to a category
    final docType = json['type'] ?? 'general';
    final category = _typeToCategory(docType);

    return DocumentModel(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      type: docType,
      category: category,
      uploadDate: json['uploadDate'] != null
          ? DateTime.tryParse(json['uploadDate']) ?? DateTime.now()
          : (json['createdAt'] != null
              ? DateTime.tryParse(json['createdAt']) ?? DateTime.now()
              : DateTime.now()),
      expiryDate: expiry,
      fileUrl: json['viewUrl'],
      fileSize: json['fileSize'] ?? 0,
      tags: json['tags'] != null
          ? List<String>.from(json['tags'])
          : <String>[],
      status: status,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'type': type,
        'category': category,
        'uploadDate': uploadDate.toIso8601String(),
        'expiryDate': expiryDate?.toIso8601String(),
        'fileUrl': fileUrl,
        'fileSize': fileSize,
        'tags': tags,
        'status': status,
      };

  static String _typeToCategory(String type) {
    switch (type.toLowerCase()) {
      case 'id':
      case 'identity':
        return 'Identity';
      case 'academic':
      case 'education':
        return 'Education';
      case 'financial':
      case 'finance':
        return 'Finance';
      case 'insurance':
        return 'Insurance';
      case 'medical':
        return 'Medical';
      case 'legal':
        return 'Legal';
      default:
        return 'Other';
    }
  }

  bool get isExpired {
    if (expiryDate == null) return false;
    return expiryDate!.isBefore(DateTime.now());
  }

  bool get isExpiringSoon {
    if (expiryDate == null) return false;
    final daysUntilExpiry = expiryDate!.difference(DateTime.now()).inDays;
    return daysUntilExpiry > 0 && daysUntilExpiry <= 30;
  }

  int? get daysUntilExpiry {
    if (expiryDate == null) return null;
    return expiryDate!.difference(DateTime.now()).inDays;
  }

  String get fileSizeFormatted {
    if (fileSize < 1024) return '$fileSize B';
    if (fileSize < 1024 * 1024) return '${(fileSize / 1024).toStringAsFixed(1)} KB';
    return '${(fileSize / (1024 * 1024)).toStringAsFixed(1)} MB';
  }

  DocumentModel copyWith({
    String? id,
    String? name,
    String? type,
    String? category,
    DateTime? uploadDate,
    DateTime? expiryDate,
    String? fileUrl,
    String? localPath,
    String? thumbnailUrl,
    int? fileSize,
    List<String>? tags,
    bool? isOfflineAvailable,
    String? status,
  }) {
    return DocumentModel(
      id: id ?? this.id,
      name: name ?? this.name,
      type: type ?? this.type,
      category: category ?? this.category,
      uploadDate: uploadDate ?? this.uploadDate,
      expiryDate: expiryDate ?? this.expiryDate,
      fileUrl: fileUrl ?? this.fileUrl,
      localPath: localPath ?? this.localPath,
      thumbnailUrl: thumbnailUrl ?? this.thumbnailUrl,
      fileSize: fileSize ?? this.fileSize,
      tags: tags ?? this.tags,
      isOfflineAvailable: isOfflineAvailable ?? this.isOfflineAvailable,
      status: status ?? this.status,
    );
  }
}
