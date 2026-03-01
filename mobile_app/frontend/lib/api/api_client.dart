import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'api_config.dart';

/// Centralized HTTP client that handles authentication headers,
/// JSON encoding/decoding, and token persistence.
class ApiClient {
  static String? _token;
  static const String _tokenKey = 'auth_token';

  // ─── Token management ───

  /// Load persisted token from SharedPreferences.
  static Future<void> loadToken() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString(_tokenKey);
  }

  /// Persist and set the JWT token.
  static Future<void> setToken(String token) async {
    _token = token;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_tokenKey, token);
  }

  /// Clear the stored token (logout).
  static Future<void> clearToken() async {
    _token = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
  }

  /// Current token (may be null).
  static String? get token => _token;

  /// Whether we currently hold a token.
  static bool get hasToken => _token != null && _token!.isNotEmpty;

  // ─── Header helpers ───

  static Map<String, String> _headers({bool auth = true}) {
    final headers = <String, String>{
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
    if (auth && _token != null) {
      headers['Authorization'] = 'Bearer $_token';
    }
    return headers;
  }

  static Map<String, String> _authOnlyHeaders() {
    final headers = <String, String>{
      'Accept': 'application/json',
    };
    if (_token != null) {
      headers['Authorization'] = 'Bearer $_token';
    }
    return headers;
  }

  // ─── Core HTTP methods ───

  /// GET request – returns decoded JSON body.
  static Future<ApiResponse> get(
    String path, {
    Map<String, String>? queryParams,
    bool auth = true,
  }) async {
    try {
      final uri = _buildUri(path, queryParams);
      final response = await http
          .get(uri, headers: _headers(auth: auth))
          .timeout(Duration(seconds: ApiConfig.receiveTimeout));
      return _handleResponse(response);
    } catch (e) {
      return ApiResponse.error(_friendlyError(e));
    }
  }

  /// POST request with JSON body.
  static Future<ApiResponse> post(
    String path, {
    Map<String, dynamic>? body,
    bool auth = true,
  }) async {
    try {
      final uri = _buildUri(path);
      final response = await http
          .post(uri, headers: _headers(auth: auth), body: jsonEncode(body ?? {}))
          .timeout(Duration(seconds: ApiConfig.receiveTimeout));
      return _handleResponse(response);
    } catch (e) {
      return ApiResponse.error(_friendlyError(e));
    }
  }

  /// PUT request with JSON body.
  static Future<ApiResponse> put(
    String path, {
    Map<String, dynamic>? body,
    bool auth = true,
  }) async {
    try {
      final uri = _buildUri(path);
      final response = await http
          .put(uri, headers: _headers(auth: auth), body: jsonEncode(body ?? {}))
          .timeout(Duration(seconds: ApiConfig.receiveTimeout));
      return _handleResponse(response);
    } catch (e) {
      return ApiResponse.error(_friendlyError(e));
    }
  }

  /// PATCH request with JSON body.
  static Future<ApiResponse> patch(
    String path, {
    Map<String, dynamic>? body,
    bool auth = true,
  }) async {
    try {
      final uri = _buildUri(path);
      final response = await http
          .patch(uri, headers: _headers(auth: auth), body: jsonEncode(body ?? {}))
          .timeout(Duration(seconds: ApiConfig.receiveTimeout));
      return _handleResponse(response);
    } catch (e) {
      return ApiResponse.error(_friendlyError(e));
    }
  }

  /// DELETE request.
  static Future<ApiResponse> delete(
    String path, {
    bool auth = true,
  }) async {
    try {
      final uri = _buildUri(path);
      final response = await http
          .delete(uri, headers: _headers(auth: auth))
          .timeout(Duration(seconds: ApiConfig.receiveTimeout));
      return _handleResponse(response);
    } catch (e) {
      return ApiResponse.error(_friendlyError(e));
    }
  }

  /// Multipart file upload (POST).
  /// Automatically detects and sets the correct MIME type from file extension.
  static Future<ApiResponse> uploadFile(
    String path, {
    required File file,
    required String fileFieldName,
    Map<String, String>? fields,
  }) async {
    try {
      final uri = _buildUri(path);
      final request = http.MultipartRequest('POST', uri);

      // Auth header
      if (_token != null) {
        request.headers['Authorization'] = 'Bearer $_token';
      }

      // Detect correct MIME type from file extension
      final contentType = _detectMediaType(file.path);

      // Attach file with explicit content type
      request.files.add(await http.MultipartFile.fromPath(
        fileFieldName,
        file.path,
        contentType: contentType,
      ));

      // Attach form fields
      if (fields != null) {
        request.fields.addAll(fields);
      }

      final streamed = await request.send().timeout(
            Duration(seconds: ApiConfig.uploadTimeout),
          );
      final response = await http.Response.fromStream(streamed);
      return _handleResponse(response);
    } catch (e) {
      return ApiResponse.error(_friendlyError(e));
    }
  }

  /// Detect the correct MediaType from a file path's extension.
  /// This prevents Flutter from sending 'application/octet-stream'
  /// for known file types like PDF, JPEG, PNG.
  static MediaType _detectMediaType(String filePath) {
    final ext = filePath.split('.').last.toLowerCase();
    switch (ext) {
      case 'pdf':
        return MediaType('application', 'pdf');
      case 'jpg':
      case 'jpeg':
        return MediaType('image', 'jpeg');
      case 'png':
        return MediaType('image', 'png');
      case 'webp':
        return MediaType('image', 'webp');
      case 'tiff':
      case 'tif':
        return MediaType('image', 'tiff');
      case 'bmp':
        return MediaType('image', 'bmp');
      case 'doc':
        return MediaType('application', 'msword');
      case 'docx':
        return MediaType('application', 'vnd.openxmlformats-officedocument.wordprocessingml.document');
      default:
        return MediaType('application', 'octet-stream');
    }
  }

  // ─── Internal helpers ───

  static Uri _buildUri(String path, [Map<String, String>? queryParams]) {
    final fullPath = '${ApiConfig.apiPrefix}$path';
    final uri = Uri.parse('${ApiConfig.baseUrl}$fullPath');
    if (queryParams != null && queryParams.isNotEmpty) {
      return uri.replace(queryParameters: queryParams);
    }
    return uri;
  }

  static ApiResponse _handleResponse(http.Response response) {
    Map<String, dynamic> body;
    try {
      body = jsonDecode(response.body) as Map<String, dynamic>;
    } catch (_) {
      body = {'error': response.body};
    }

    if (response.statusCode >= 200 && response.statusCode < 300) {
      return ApiResponse(
        success: body['success'] ?? true,
        data: body,
        statusCode: response.statusCode,
        message: body['message'] as String?,
      );
    } else {
      return ApiResponse(
        success: false,
        data: body,
        statusCode: response.statusCode,
        message: body['message'] as String? ??
            body['error'] as String? ??
            'Request failed (${response.statusCode})',
      );
    }
  }

  static String _friendlyError(Object e) {
    if (e is SocketException) {
      return 'No internet connection. Please check your network.';
    }
    if (e.toString().contains('TimeoutException')) {
      return 'Request timed out. Please try again.';
    }
    return 'Something went wrong. Please try again.';
  }
}

/// Generic API response wrapper.
class ApiResponse {
  final bool success;
  final Map<String, dynamic>? data;
  final int statusCode;
  final String? message;

  const ApiResponse({
    required this.success,
    this.data,
    this.statusCode = 0,
    this.message,
  });

  factory ApiResponse.error(String message) =>
      ApiResponse(success: false, message: message);
}
