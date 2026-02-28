import 'dart:io';
import 'package:flutter/material.dart';
import '../models/document_model.dart';
import '../api/api_client.dart';
import '../api/endpoints.dart';

class DocumentProvider extends ChangeNotifier {
  List<DocumentModel> _documents = [];
  bool _isLoading = false;
  String _searchQuery = '';
  String _selectedCategory = 'All';
  String _viewMode = 'grid'; // 'grid' or 'list'
  String? _error;

  // Getters
  List<DocumentModel> get documents => _filteredDocuments;
  List<DocumentModel> get allDocuments => _documents;
  bool get isLoading => _isLoading;
  String get searchQuery => _searchQuery;
  String get selectedCategory => _selectedCategory;
  String get viewMode => _viewMode;
  String? get error => _error;

  List<DocumentModel> get _filteredDocuments {
    var filtered = _documents;

    if (_selectedCategory != 'All') {
      filtered = filtered.where((d) => d.category == _selectedCategory).toList();
    }

    if (_searchQuery.isNotEmpty) {
      final query = _searchQuery.toLowerCase();
      filtered = filtered.where((d) {
        return d.name.toLowerCase().contains(query) ||
            d.type.toLowerCase().contains(query) ||
            d.tags.any((t) => t.toLowerCase().contains(query));
      }).toList();
    }

    return filtered;
  }

  int get totalDocuments => _documents.length;

  List<DocumentModel> get expiringDocuments =>
      _documents.where((d) => d.isExpiringSoon).toList();

  List<DocumentModel> get expiredDocuments =>
      _documents.where((d) => d.isExpired).toList();

  List<DocumentModel> get recentDocuments {
    final sorted = List<DocumentModel>.from(_documents)
      ..sort((a, b) => b.uploadDate.compareTo(a.uploadDate));
    return sorted.take(5).toList();
  }

  DocumentModel? getDocumentById(String id) {
    try {
      return _documents.firstWhere((d) => d.id == id);
    } catch (_) {
      return null;
    }
  }

  Future<void> fetchDocuments() async {
    _isLoading = true;
    notifyListeners();

    final res = await ApiClient.get(Endpoints.documentList);

    if (res.success && res.data?['documents'] != null) {
      final list = res.data!['documents'] as List;
      _documents = list
          .map((d) => DocumentModel.fromJson(d as Map<String, dynamic>))
          .toList();
    }
    _isLoading = false;
    notifyListeners();
  }

  void setSearchQuery(String query) {
    _searchQuery = query;
    notifyListeners();
  }

  void setCategory(String category) {
    _selectedCategory = category;
    notifyListeners();
  }

  void toggleViewMode() {
    _viewMode = _viewMode == 'grid' ? 'list' : 'grid';
    notifyListeners();
  }

  Future<bool> deleteDocument(String id) async {
    final res = await ApiClient.delete(Endpoints.documentDelete(id));
    if (res.success) {
      _documents.removeWhere((d) => d.id == id);
      notifyListeners();
      return true;
    }
    return false;
  }

  /// Upload a document file to the backend.
  /// [file] is the actual file on disk.
  /// [name] is the display name, [docType] the backend type string,
  /// [hasExpiry] + [expiryDate] for expiry tracking.
  Future<bool> uploadDocument({
    required File file,
    required String name,
    required String docType,
    bool hasExpiry = false,
    DateTime? expiryDate,
  }) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    final fields = <String, String>{
      'name': name,
      'type': docType,
      'hasExpiry': hasExpiry.toString(),
    };
    if (expiryDate != null) {
      fields['expiryDate'] = expiryDate.toIso8601String();
    }

    final res = await ApiClient.uploadFile(
      Endpoints.documentUpload,
      file: file,
      fileFieldName: 'file',
      fields: fields,
    );

    if (res.success && res.data?['document'] != null) {
      final doc = DocumentModel.fromJson(
          res.data!['document'] as Map<String, dynamic>);
      _documents.insert(0, doc);
    } else {
      _error = res.message ?? 'Upload failed';
    }

    _isLoading = false;
    notifyListeners();
    return res.success;
  }

  /// Get a pre-signed view URL for a document.
  Future<String?> getViewUrl(String documentId) async {
    final res = await ApiClient.get(Endpoints.documentGet(documentId));
    if (res.success) {
      return res.data?['viewUrl'] as String?;
    }
    return null;
  }
}
