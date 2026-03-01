import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:provider/provider.dart';
import 'package:gap/gap.dart';
import '../../config/theme.dart';
import '../../config/constants.dart';
import '../../providers/chat_provider.dart';
import '../../models/chat_message_model.dart';
import '../../widgets/chat/message_bubble.dart';
import '../../widgets/chat/chat_input_field.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final ScrollController _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<ChatProvider>().loadChatHistory().then((_) {
        _scrollToBottom();
      });
    });
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  void _scrollToBottom() {
    Future.delayed(const Duration(milliseconds: 100), () {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  void _handleSend(String message) {
    if (message.trim().isEmpty) return;
    context.read<ChatProvider>().sendMessage(message).then((_) {
      _scrollToBottom();
    });
    _scrollToBottom();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;
    final chatProvider = context.watch<ChatProvider>();
    final messages = chatProvider.messages;

    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            Container(
              width: 36,
              height: 36,
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [AppTheme.brand600, AppTheme.brand400],
                ),
                borderRadius: BorderRadius.circular(10),
              ),
              child: const Icon(
                Icons.smart_toy_outlined,
                color: Colors.white,
                size: 20,
              ),
            ),
            const Gap(12),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'AI Assistant',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
                ),
                Text(
                  chatProvider.isTyping ? 'Typing...' : 'Online',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: chatProvider.isTyping
                        ? AppTheme.brand600
                        : const Color(0xFF20C997),
                    fontWeight: FontWeight.w500,
                    fontSize: 11,
                  ),
                ),
              ],
            ),
          ],
        ),
        automaticallyImplyLeading: false,
        actions: [
          IconButton(
            onPressed: () => _showClearDialog(context),
            icon: const Icon(Icons.delete_sweep_outlined, size: 22),
          ),
          const SizedBox(width: 4),
        ],
      ),
      body: Column(
        children: [
          // Messages
          Expanded(
            child: messages.isEmpty
                ? _buildWelcomeView(context)
                : ListView.builder(
                    controller: _scrollController,
                    padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
                    itemCount: messages.length + (chatProvider.isTyping ? 1 : 0),
                    itemBuilder: (context, index) {
                      if (index == messages.length && chatProvider.isTyping) {
                        return Padding(
                          padding: const EdgeInsets.only(bottom: 8),
                          child: MessageBubble(
                            message: ChatMessageModel(
                              id: 'typing',
                              content: '',
                              isUser: false,
                              isLoading: true,
                              timestamp: DateTime.now(),
                            ),
                          ),
                        );
                      }

                      final msg = messages[index];
                      return Padding(
                        padding: const EdgeInsets.only(bottom: 8),
                        child: MessageBubble(
                          message: msg,
                        ),
                      )
                          .animate()
                          .fadeIn(duration: 300.ms)
                          .slideY(
                            begin: 0.1,
                            duration: 300.ms,
                            curve: Curves.easeOut,
                          );
                    },
                  ),
          ),

          // Suggested Questions
          if (messages.length <= 1) _buildSuggestions(context),

          // Input
          ChatInputField(
            onSend: _handleSend,
          ),
        ],
      ),
    );
  }

  Widget _buildWelcomeView(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return Center(
      child: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
            Container(
              width: 80,
              height: 80,
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    AppTheme.brand600.withOpacity(0.1),
                    AppTheme.brand400.withOpacity(0.05),
                  ],
                ),
                borderRadius: BorderRadius.circular(24),
              ),
              child: Icon(
                Icons.smart_toy_outlined,
                size: 40,
                color: AppTheme.brand600.withOpacity(0.6),
              ),
            )
                .animate()
                .fadeIn(duration: 500.ms)
                .scale(begin: const Offset(0.8, 0.8)),
            const Gap(20),
            Text(
              'Ask me anything about\nyour documents',
              style: theme.textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.w700,
              ),
              textAlign: TextAlign.center,
            ).animate().fadeIn(delay: 100.ms, duration: 400.ms),
            const Gap(8),
            Text(
              'I can help you find information, answer questions,\nand analyze your uploaded documents.',
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurface.withOpacity(0.5),
              ),
              textAlign: TextAlign.center,
            ).animate().fadeIn(delay: 200.ms, duration: 400.ms),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSuggestions(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return Container(
      padding: const EdgeInsets.fromLTRB(16, 0, 16, 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Text(
              'Suggested questions',
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurface.withOpacity(0.4),
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: AppConstants.suggestedQuestions.map((q) {
              return InkWell(
                onTap: () => _handleSend(q),
                borderRadius: BorderRadius.circular(20),
                child: Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                  decoration: BoxDecoration(
                    color: isDark
                        ? AppTheme.brand400.withOpacity(0.08)
                        : AppTheme.brand50,
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(
                      color: AppTheme.brand600.withOpacity(0.15),
                    ),
                  ),
                  child: Text(
                    q,
                    style: TextStyle(
                      color: AppTheme.brand600,
                      fontSize: 12,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
              );
            }).toList(),
          ),
        ],
      ),
    ).animate().fadeIn(delay: 300.ms, duration: 400.ms);
  }

  void _showClearDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Text('Clear Chat'),
        content: const Text('This will delete all messages. Continue?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () async {
              await context.read<ChatProvider>().clearChat();
              if (context.mounted) Navigator.pop(ctx);
            },
            child: const Text(
              'Clear',
              style: TextStyle(color: Color(0xFFFA5252)),
            ),
          ),
        ],
      ),
    );
  }
}
