import 'package:flutter/material.dart';
import '../../config/theme.dart';
import '../../models/document_model.dart';

class DocumentCard extends StatelessWidget {
  final DocumentModel document;
  final VoidCallback? onTap;
  final VoidCallback? onLongPress;
  final bool isGridView;

  const DocumentCard({
    super.key,
    required this.document,
    this.onTap,
    this.onLongPress,
    this.isGridView = true,
  });

  IconData _getDocumentIcon() {
    switch (document.category) {
      case 'Identity':
        return Icons.badge_outlined;
      case 'Education':
        return Icons.school_outlined;
      case 'Finance':
        return Icons.account_balance_outlined;
      case 'Insurance':
        return Icons.health_and_safety_outlined;
      case 'Medical':
        return Icons.local_hospital_outlined;
      case 'Legal':
        return Icons.gavel_outlined;
      default:
        return Icons.description_outlined;
    }
  }

  Color _getCategoryColor() {
    switch (document.category) {
      case 'Identity':
        return AppTheme.brand600;
      case 'Education':
        return const Color(0xFF7C3AED);
      case 'Finance':
        return AppTheme.success500;
      case 'Insurance':
        return const Color(0xFFEC4899);
      case 'Medical':
        return AppTheme.error500;
      case 'Legal':
        return AppTheme.warning500;
      default:
        return AppTheme.neutral500;
    }
  }

  Widget _buildStatusBadge(BuildContext context) {
    if (document.isExpired) {
      return _StatusChip(
        label: 'Expired',
        color: AppTheme.error500,
        bgColor: AppTheme.error50,
      );
    }
    if (document.isExpiringSoon) {
      return _StatusChip(
        label: '${document.daysUntilExpiry}d left',
        color: AppTheme.warning700,
        bgColor: AppTheme.warning50,
      );
    }
    return const SizedBox.shrink();
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final categoryColor = _getCategoryColor();

    if (isGridView) {
      return _buildGridCard(context, isDark, categoryColor);
    }
    return _buildListCard(context, isDark, categoryColor);
  }

  Widget _buildGridCard(BuildContext context, bool isDark, Color categoryColor) {
    return GestureDetector(
      onTap: onTap,
      onLongPress: onLongPress,
      child: Container(
        decoration: BoxDecoration(
          color: isDark ? const Color(0xFF1A1C2A) : Colors.white,
          borderRadius: BorderRadius.circular(AppTheme.radiusMd),
          border: Border.all(
            color: isDark
                ? const Color(0xFF2D3050)
                : AppTheme.neutral200,
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Thumbnail area
            Container(
              height: 100,
              width: double.infinity,
              decoration: BoxDecoration(
                color: categoryColor.withOpacity(isDark ? 0.15 : 0.08),
                borderRadius: const BorderRadius.vertical(
                  top: Radius.circular(AppTheme.radiusMd),
                ),
              ),
              child: Stack(
                children: [
                  Center(
                    child: Icon(
                      _getDocumentIcon(),
                      size: 40,
                      color: categoryColor.withOpacity(0.6),
                    ),
                  ),
                  Positioned(
                    top: 8,
                    right: 8,
                    child: _buildStatusBadge(context),
                  ),
                  if (document.isOfflineAvailable)
                    Positioned(
                      top: 8,
                      left: 8,
                      child: Container(
                        padding: const EdgeInsets.all(4),
                        decoration: BoxDecoration(
                          color: isDark
                              ? Colors.black.withOpacity(0.3)
                              : Colors.white.withOpacity(0.9),
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: Icon(
                          Icons.offline_pin,
                          size: 14,
                          color: AppTheme.success500,
                        ),
                      ),
                    ),
                ],
              ),
            ),
            // Info area
            Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    document.name,
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          fontWeight: FontWeight.w600,
                        ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      Container(
                        width: 6,
                        height: 6,
                        decoration: BoxDecoration(
                          color: categoryColor,
                          shape: BoxShape.circle,
                        ),
                      ),
                      const SizedBox(width: 6),
                      Expanded(
                        child: Text(
                          document.category,
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                color: Theme.of(context)
                                    .colorScheme
                                    .onSurface
                                    .withOpacity(0.5),
                              ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      Text(
                        document.fileSizeFormatted,
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: Theme.of(context)
                                  .colorScheme
                                  .onSurface
                                  .withOpacity(0.4),
                              fontSize: 11,
                            ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildListCard(BuildContext context, bool isDark, Color categoryColor) {
    return GestureDetector(
      onTap: onTap,
      onLongPress: onLongPress,
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: isDark ? const Color(0xFF1A1C2A) : Colors.white,
          borderRadius: BorderRadius.circular(AppTheme.radiusMd),
          border: Border.all(
            color: isDark
                ? const Color(0xFF2D3050)
                : AppTheme.neutral200,
          ),
        ),
        child: Row(
          children: [
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: categoryColor.withOpacity(isDark ? 0.15 : 0.08),
                borderRadius: BorderRadius.circular(AppTheme.radiusSm),
              ),
              child: Icon(
                _getDocumentIcon(),
                size: 24,
                color: categoryColor,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    document.name,
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          fontWeight: FontWeight.w600,
                        ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 2),
                  Row(
                    children: [
                      Text(
                        document.category,
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: Theme.of(context)
                                  .colorScheme
                                  .onSurface
                                  .withOpacity(0.5),
                            ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        '•',
                        style: TextStyle(
                          color: Theme.of(context)
                              .colorScheme
                              .onSurface
                              .withOpacity(0.3),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        document.fileSizeFormatted,
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: Theme.of(context)
                                  .colorScheme
                                  .onSurface
                                  .withOpacity(0.4),
                            ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            _buildStatusBadge(context),
            if (document.isOfflineAvailable)
              Padding(
                padding: const EdgeInsets.only(left: 8),
                child: Icon(
                  Icons.offline_pin,
                  size: 18,
                  color: AppTheme.success500,
                ),
              ),
            const SizedBox(width: 4),
            Icon(
              Icons.chevron_right,
              size: 20,
              color: Theme.of(context).colorScheme.onSurface.withOpacity(0.3),
            ),
          ],
        ),
      ),
    );
  }
}

class _StatusChip extends StatelessWidget {
  final String label;
  final Color color;
  final Color bgColor;

  const _StatusChip({
    required this.label,
    required this.color,
    required this.bgColor,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(6),
      ),
      child: Text(
        label,
        style: TextStyle(
          color: color,
          fontSize: 10,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
}
