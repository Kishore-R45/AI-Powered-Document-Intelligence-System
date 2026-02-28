import 'package:flutter/material.dart';
import '../models/chat_message_model.dart';
import '../api/api_client.dart';
import '../api/endpoints.dart';

class ChatProvider extends ChangeNotifier {
  List<ChatMessageModel> _messages = [];
  bool _isLoading = false;
  bool _isTyping = false;

  // Getters
  List<ChatMessageModel> get messages => _messages;
  bool get isLoading => _isLoading;
  bool get isTyping => _isTyping;

  Future<void> loadChatHistory() async {
    _isLoading = true;
    notifyListeners();

    final res = await ApiClient.get(
      Endpoints.chatHistory,
      queryParams: {'limit': '50'},
    );

    if (res.success && res.data?['messages'] != null) {
      final list = res.data!['messages'] as List;
      _messages = list
          .map((m) => ChatMessageModel.fromJson(m as Map<String, dynamic>))
          .toList();
    }
    _isLoading = false;
    notifyListeners();
  }

  Future<void> sendMessage(String content) async {
    // Add user message optimistically
    final userMessage = ChatMessageModel(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      content: content,
      isUser: true,
      timestamp: DateTime.now(),
    );
    _messages.add(userMessage);
    notifyListeners();

    // Show typing indicator
    _isTyping = true;
    notifyListeners();

    // Send to backend
    final res = await ApiClient.post(
      Endpoints.chatQuery,
      body: {'question': content},
    );

    _isTyping = false;

    if (res.success) {
      final answer = res.data?['answer'] as String? ?? 'No answer found.';
      final sourcesRaw = res.data?['sources'] as List? ?? [];
      final sources = sourcesRaw
          .map((s) => SourceReference.fromJson(s as Map<String, dynamic>))
          .toList();

      final aiResponse = ChatMessageModel(
        id: (DateTime.now().millisecondsSinceEpoch + 1).toString(),
        content: answer,
        isUser: false,
        timestamp: DateTime.now(),
        sources: sources,
      );
      _messages.add(aiResponse);
    } else {
      final errorMsg = ChatMessageModel(
        id: (DateTime.now().millisecondsSinceEpoch + 1).toString(),
        content: res.message ?? 'Failed to get a response. Please try again.',
        isUser: false,
        timestamp: DateTime.now(),
      );
      _messages.add(errorMsg);
    }
    notifyListeners();
  }

  Future<void> clearChat() async {
    await ApiClient.delete(Endpoints.chatHistory);
    _messages.clear();
    notifyListeners();
  }
}
