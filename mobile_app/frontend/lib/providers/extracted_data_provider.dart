import 'package:flutter/material.dart';
import '../models/extracted_data_model.dart';
import '../api/api_client.dart';
import '../api/endpoints.dart';

class ExtractedDataProvider extends ChangeNotifier {
  List<ExtractedDataModel> _extractedDataList = [];
  bool _isLoading = false;
  String _searchQuery = '';

  // Getters
  List<ExtractedDataModel> get extractedDataList => _filteredData;
  List<ExtractedDataModel> get allExtractedData => _extractedDataList;
  bool get isLoading => _isLoading;
  String get searchQuery => _searchQuery;

  List<ExtractedDataModel> get _filteredData {
    if (_searchQuery.isEmpty) return _extractedDataList;

    final query = _searchQuery.toLowerCase();
    return _extractedDataList.where((item) {
      return item.documentName.toLowerCase().contains(query) ||
          item.documentType.toLowerCase().contains(query) ||
          item.data.keys.any((k) => k.toLowerCase().contains(query)) ||
          item.data.values.any((v) => v.toLowerCase().contains(query));
    }).toList();
  }

  Map<String, List<ExtractedDataModel>> get groupedByCategory {
    final map = <String, List<ExtractedDataModel>>{};
    for (final item in _extractedDataList) {
      map.putIfAbsent(item.category, () => []).add(item);
    }
    return map;
  }

  ExtractedDataModel? getByDocumentId(String documentId) {
    try {
      return _extractedDataList.firstWhere((d) => d.documentId == documentId);
    } catch (_) {
      return null;
    }
  }

  /// Fetches all documents and builds extracted-data entries from their metadata.
  Future<void> fetchExtractedData() async {
    _isLoading = true;
    notifyListeners();

    final res = await ApiClient.get(Endpoints.documentList);

    if (res.success && res.data?['documents'] != null) {
      final docs = res.data!['documents'] as List;
      _extractedDataList = docs.map((d) {
        final doc = d as Map<String, dynamic>;
        final id = (doc['_id'] ?? doc['id'] ?? '').toString();
        final name = doc['name'] ?? doc['originalName'] ?? 'Untitled';
        final docType = doc['docType'] ?? doc['type'] ?? 'other';
        final extractedText = doc['extractedText'] ?? '';

        // Build key-value data map from document metadata
        final Map<String, String> data = {};
        if (extractedText.toString().isNotEmpty) {
          // Provide a truncated preview of the extracted text
          final text = extractedText.toString();
          data['Extracted Text'] =
              text.length > 500 ? '${text.substring(0, 500)}...' : text;
        }
        if (doc['pageCount'] != null) {
          data['Pages'] = doc['pageCount'].toString();
        }
        if (doc['fileSize'] != null) {
          final bytes = int.tryParse(doc['fileSize'].toString()) ?? 0;
          data['File Size'] = bytes > 1048576
              ? '${(bytes / 1048576).toStringAsFixed(1)} MB'
              : '${(bytes / 1024).toStringAsFixed(1)} KB';
        }
        if (doc['expiryDate'] != null) {
          data['Expiry Date'] = doc['expiryDate'].toString().split('T').first;
        }
        data['Document Type'] = docType.toString();

        // Map type to category
        String category;
        switch (docType.toString().toLowerCase()) {
          case 'aadhaar':
          case 'pan':
          case 'passport':
          case 'driving_license':
            category = 'Identity';
            break;
          case 'marksheet':
          case 'degree':
          case 'certificate':
            category = 'Education';
            break;
          case 'insurance':
          case 'medical':
            category = 'Medical';
            break;
          default:
            category = 'Other';
        }

        return ExtractedDataModel(
          id: 'ext_$id',
          documentId: id,
          documentName: name.toString(),
          documentType: docType.toString(),
          category: category,
          data: data,
          extractedAt:
              DateTime.tryParse(doc['createdAt']?.toString() ?? '') ??
                  DateTime.now(),
        );
      }).toList();
    }

    _isLoading = false;
    notifyListeners();
  }

  /// Fetch extracted text for a single document
  Future<ExtractedDataModel?> fetchForDocument(String documentId) async {
    final res = await ApiClient.get(Endpoints.documentGet(documentId));
    if (res.success && res.data?['document'] != null) {
      final doc = res.data!['document'] as Map<String, dynamic>;
      final name = doc['name'] ?? doc['originalName'] ?? 'Untitled';
      final docType = doc['docType'] ?? doc['type'] ?? 'other';
      final extractedText = doc['extractedText'] ?? '';

      final Map<String, String> data = {};
      if (extractedText.toString().isNotEmpty) {
        data['Extracted Text'] = extractedText.toString();
      }
      if (doc['pageCount'] != null) data['Pages'] = doc['pageCount'].toString();
      data['Document Type'] = docType.toString();

      final model = ExtractedDataModel(
        id: 'ext_$documentId',
        documentId: documentId,
        documentName: name.toString(),
        documentType: docType.toString(),
        category: 'Other',
        data: data,
        extractedAt:
            DateTime.tryParse(doc['createdAt']?.toString() ?? '') ??
                DateTime.now(),
      );

      // Update local cache
      final idx = _extractedDataList.indexWhere((e) => e.documentId == documentId);
      if (idx != -1) {
        _extractedDataList[idx] = model;
      } else {
        _extractedDataList.add(model);
      }
      notifyListeners();
      return model;
    }
    return null;
  }

  void setSearchQuery(String query) {
    _searchQuery = query;
    notifyListeners();
  }
}
