import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:provider/provider.dart';
import 'package:gap/gap.dart';
import 'package:open_filex/open_filex.dart';
import '../../config/theme.dart';
import '../../models/document_model.dart';
import '../../providers/document_provider.dart';
import '../../providers/extracted_data_provider.dart';
import '../../services/local_storage_service.dart';
import '../../widgets/common/custom_card.dart';
import '../../widgets/common/custom_button.dart';

class DocumentViewerScreen extends StatelessWidget {
  final DocumentModel document;

  const DocumentViewerScreen({super.key, required this.document});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return Scaffold(
      body: CustomScrollView(
        slivers: [
          // ─── Collapsing App Bar with Document Preview ───
          SliverAppBar(
            expandedHeight: 260,
            pinned: true,
            backgroundColor: _getCategoryColor(document.category),
            leading: IconButton(
              onPressed: () => Navigator.pop(context),
              icon: Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.black.withOpacity(0.2),
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.arrow_back, color: Colors.white, size: 20),
              ),
            ),
            actions: [
              IconButton(
                onPressed: () => _openDocument(context),
                icon: Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.black.withOpacity(0.2),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(Icons.download_outlined, color: Colors.white, size: 20),
                ),
                tooltip: 'Download',
              ),
              IconButton(
                onPressed: () {},
                icon: Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.black.withOpacity(0.2),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(Icons.share, color: Colors.white, size: 20),
                ),
                tooltip: 'Share',
              ),
              IconButton(
                onPressed: () {},
                icon: Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.black.withOpacity(0.2),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(Icons.more_vert, color: Colors.white, size: 20),
                ),
              ),
              const SizedBox(width: 4),
            ],
            flexibleSpace: FlexibleSpaceBar(
              background: Container(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topCenter,
                    end: Alignment.bottomCenter,
                    colors: [
                      _getCategoryColor(document.category),
                      _getCategoryColor(document.category).withOpacity(0.8),
                    ],
                  ),
                ),
                child: Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Gap(40),
                      Container(
                        width: 80,
                        height: 100,
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.15),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(
                            color: Colors.white.withOpacity(0.2),
                          ),
                        ),
                        child: Icon(
                          _getFileIcon(document.type),
                          size: 40,
                          color: Colors.white.withOpacity(0.8),
                        ),
                      )
                          .animate()
                          .fadeIn(duration: 500.ms)
                          .scale(begin: const Offset(0.8, 0.8)),
                      const Gap(12),
                      Text(
                        document.type.toUpperCase(),
                        style: TextStyle(
                          color: Colors.white.withOpacity(0.7),
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          letterSpacing: 1.5,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),

          // ─── Document Details ───
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Title & Category
                  Text(
                    document.name,
                    style: theme.textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ).animate().fadeIn(duration: 400.ms),

                  const Gap(8),

                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: _getCategoryColor(document.category)
                              .withOpacity(0.1),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text(
                          document.category,
                          style: TextStyle(
                            color: _getCategoryColor(document.category),
                            fontWeight: FontWeight.w600,
                            fontSize: 12,
                          ),
                        ),
                      ),
                      const Gap(8),
                      if (document.status.isNotEmpty)
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(
                            color: _getStatusColor(document.status)
                                .withOpacity(0.1),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text(
                            document.status,
                            style: TextStyle(
                              color: _getStatusColor(document.status),
                              fontWeight: FontWeight.w600,
                              fontSize: 12,
                            ),
                          ),
                        ),
                    ],
                  ).animate().fadeIn(delay: 100.ms, duration: 400.ms),

                  const Gap(24),

                  // ─── Metadata Cards ───
                  _buildInfoSection(context),

                  const Gap(24),

                  // ─── Extracted Data Button ───
                  Consumer<ExtractedDataProvider>(
                    builder: (ctx, edProvider, _) {
                      final hasData = edProvider.extractedDataList
                          .any((e) => e.documentId == document.id);
                      if (!hasData) return const SizedBox.shrink();

                      return CustomButton(
                        text: 'View Extracted Data',
                        leftIcon: Icons.table_chart_outlined,
                        variant: ButtonVariant.outline,
                        onPressed: () {
                          Navigator.pushNamed(
                            context,
                            '/document-data',
                            arguments: document,
                          );
                        },
                      ).animate().fadeIn(delay: 300.ms, duration: 400.ms);
                    },
                  ),

                  const Gap(16),

                  // ─── Action Buttons ───
                  _buildActions(context),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInfoSection(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    final items = [
      _InfoItem('File Size', document.fileSizeFormatted, Icons.storage_outlined),
      _InfoItem('File Type', document.type.toUpperCase(), Icons.insert_drive_file_outlined),
      _InfoItem('Uploaded', _formatDate(document.uploadDate), Icons.calendar_today_outlined),
      if (document.expiryDate != null)
        _InfoItem('Expires', _formatDate(document.expiryDate!), Icons.schedule_outlined),
    ];

    return CustomCard(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: items.asMap().entries.map((entry) {
          final item = entry.value;
          final isLast = entry.key == items.length - 1;
          return Column(
            children: [
              Row(
                children: [
                  Container(
                    width: 36,
                    height: 36,
                    decoration: BoxDecoration(
                      color: isDark
                          ? AppTheme.brand400.withOpacity(0.1)
                          : AppTheme.brand50,
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Icon(item.icon, size: 18, color: AppTheme.brand600),
                  ),
                  const Gap(12),
                  Text(
                    item.label,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: theme.colorScheme.onSurface.withOpacity(0.5),
                    ),
                  ),
                  const Spacer(),
                  Text(
                    item.value,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
              if (!isLast) ...[
                const Gap(12),
                Divider(
                  height: 1,
                  color: theme.colorScheme.onSurface.withOpacity(0.06),
                ),
                const Gap(12),
              ],
            ],
          );
        }).toList(),
      ),
    ).animate().fadeIn(delay: 200.ms, duration: 400.ms);
  }

  Widget _buildActions(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: CustomButton(
            text: 'View',
            leftIcon: Icons.visibility_outlined,
            variant: ButtonVariant.primary,
            onPressed: () => _openDocument(context),
          ),
        ),
        const Gap(12),
        Expanded(
          child: CustomButton(
            text: 'Delete',
            leftIcon: Icons.delete_outline,
            variant: ButtonVariant.outline,
            onPressed: () => _showDeleteDialog(context),
          ),
        ),
      ],
    ).animate().fadeIn(delay: 400.ms, duration: 400.ms);
  }

  void _openDocument(BuildContext context) async {
    // Try to open the locally-stored file using the device's default viewer
    final localPath = LocalStorageService.getDocFilePath(document.id);
    if (localPath != null && localPath.isNotEmpty) {
      final file = File(localPath);
      if (await file.exists()) {
        final result = await OpenFilex.open(localPath);
        if (result.type == ResultType.done) return;
        // If open failed, fall through to show message
      }
    }

    // No local file available — show a helpful message
    if (context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text(
              'Document file not available locally. Please re-upload to store it on this device.'),
          backgroundColor: const Color(0xFFF59F00),
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(10),
          ),
        ),
      );
    }
  }

  void _showDeleteDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Text('Delete Document'),
        content: Text('Are you sure you want to delete "${document.name}"?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () async {
              Navigator.pop(ctx);
              final success = await context
                  .read<DocumentProvider>()
                  .deleteDocument(document.id);
              if (context.mounted) {
                if (success) {
                  Navigator.pop(context);
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: const Text('Document deleted'),
                      backgroundColor: const Color(0xFF20C997),
                      behavior: SnackBarBehavior.floating,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(10),
                      ),
                    ),
                  );
                } else {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: const Text('Failed to delete document'),
                      backgroundColor: const Color(0xFFFA5252),
                      behavior: SnackBarBehavior.floating,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(10),
                      ),
                    ),
                  );
                }
              }
            },
            child: const Text(
              'Delete',
              style: TextStyle(color: Color(0xFFFA5252)),
            ),
          ),
        ],
      ),
    );
  }

  Color _getCategoryColor(String category) {
    switch (category.toLowerCase()) {
      case 'identity':
        return AppTheme.brand600;
      case 'education':
        return const Color(0xFF7C4DFF);
      case 'finance':
        return const Color(0xFF20C997);
      case 'insurance':
        return const Color(0xFFE64980);
      case 'medical':
        return const Color(0xFFFA5252);
      case 'legal':
        return const Color(0xFFF59F00);
      default:
        return AppTheme.brand600;
    }
  }

  IconData _getFileIcon(String type) {
    switch (type.toLowerCase()) {
      case 'pdf':
        return Icons.picture_as_pdf;
      case 'jpg':
      case 'jpeg':
      case 'png':
        return Icons.image;
      default:
        return Icons.description;
    }
  }

  Color _getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'active':
        return const Color(0xFF20C997);
      case 'expiring':
        return const Color(0xFFF59F00);
      case 'expired':
        return const Color(0xFFFA5252);
      default:
        return AppTheme.brand600;
    }
  }

  String _formatDate(DateTime date) {
    const months = [
      'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ];
    return '${date.day} ${months[date.month - 1]} ${date.year}';
  }
}

class _InfoItem {
  final String label;
  final String value;
  final IconData icon;
  _InfoItem(this.label, this.value, this.icon);
}
