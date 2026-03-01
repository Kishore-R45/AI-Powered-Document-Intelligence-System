import 'package:flutter/material.dart';
import '../models/document_model.dart';
import '../models/extracted_data_model.dart';
import '../api/api_client.dart';
import '../api/endpoints.dart';
import '../services/local_storage_service.dart';

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

  /// Fetch all documents and build extracted data from their extractedData field.
  /// The mobile backend stores AI-extracted key-value data in each document.
  Future<void> fetchExtractedData() async {
    _isLoading = true;
    notifyListeners();

    final res = await ApiClient.get(Endpoints.documentList);

    if (res.success && res.data?['documents'] != null) {
      final docs = res.data!['documents'] as List;
      _extractedDataList = docs.map((d) {
        final doc = DocumentModel.fromJson(d as Map<String, dynamic>);
        return ExtractedDataModel.fromDocument(doc);
      }).toList();

      // Cache offline
      await LocalStorageService.cacheAllExtractedData(_extractedDataList);
    } else {
      // Fallback to offline cache
      if (_extractedDataList.isEmpty) {
        _extractedDataList = LocalStorageService.getAllCachedExtractedData();
      }
    }

    _isLoading = false;
    notifyListeners();
  }

  /// Fetch extracted data for a single document using dedicated endpoint.
  Future<ExtractedDataModel?> fetchForDocument(String documentId) async {
    final res =
        await ApiClient.get(Endpoints.documentExtractedData(documentId));

    if (res.success && res.data != null) {
      final model = ExtractedDataModel.fromJson(res.data!);

      // Update local list
      final idx =
          _extractedDataList.indexWhere((e) => e.documentId == documentId);
      if (idx != -1) {
        _extractedDataList[idx] = model;
      } else {
        _extractedDataList.add(model);
      }

      // Cache offline
      await LocalStorageService.cacheExtractedData(documentId, model);
      notifyListeners();
      return model;
    }

    // Try offline cache
    return LocalStorageService.getCachedExtractedData(documentId);
  }

  /// Re-extract AI key-value data for a document.
  Future<bool> reExtractData(String documentId) async {
    _isLoading = true;
    notifyListeners();

    final res =
        await ApiClient.post(Endpoints.documentReExtract(documentId));

    if (res.success && res.data != null) {
      // Refresh the data
      await fetchForDocument(documentId);
    }

    _isLoading = false;
    notifyListeners();
    return res.success;
  }

  /// Delete a single key-value field from a document's extracted data.
  Future<bool> deleteField(String documentId, String fieldKey) async {
    final res = await ApiClient.post(
      Endpoints.documentDeleteField(documentId),
      body: {'key': fieldKey},
    );

    if (res.success) {
      // Update local data
      final idx = _extractedDataList.indexWhere((e) => e.documentId == documentId);
      if (idx != -1) {
        final current = _extractedDataList[idx];
        final updatedData = Map<String, String>.from(current.data);
        updatedData.remove(fieldKey);
        _extractedDataList[idx] = current.copyWith(data: updatedData);

        // Update offline cache
        await LocalStorageService.cacheExtractedData(documentId, _extractedDataList[idx]);
      }
      notifyListeners();
    }

    return res.success;
  }

  void setSearchQuery(String query) {
    _searchQuery = query;
    notifyListeners();
  }
}
