import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../config/theme.dart';

class KeyValueCard extends StatelessWidget {
  final String keyLabel;
  final String value;
  final bool isLast;
  final VoidCallback? onDelete;
  final VoidCallback? onEdit;
  final bool isSelectionMode;
  final bool isSelected;
  final ValueChanged<bool?>? onSelectionChanged;

  const KeyValueCard({
    super.key,
    required this.keyLabel,
    required this.value,
    this.isLast = false,
    this.onDelete,
    this.onEdit,
    this.isSelectionMode = false,
    this.isSelected = false,
    this.onSelectionChanged,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // ─── Selection checkbox in edit mode ───
              if (isSelectionMode) ...[
                Padding(
                  padding: const EdgeInsets.only(top: 4),
                  child: SizedBox(
                    width: 24,
                    height: 24,
                    child: Checkbox(
                      value: isSelected,
                      onChanged: onSelectionChanged,
                      activeColor: AppTheme.brand600,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(4),
                      ),
                      materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                    ),
                  ),
                ),
                const SizedBox(width: 8),
              ],
              // ─── Color bar ───
              if (!isSelectionMode)
                Container(
                  width: 4,
                  height: 32,
                  decoration: BoxDecoration(
                    color: Theme.of(context).colorScheme.primary.withOpacity(0.4),
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              if (!isSelectionMode) const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      keyLabel,
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: Theme.of(context)
                                .colorScheme
                                .onSurface
                                .withOpacity(0.5),
                            fontWeight: FontWeight.w500,
                            fontSize: 12,
                            letterSpacing: 0.3,
                          ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      value,
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                            fontWeight: FontWeight.w600,
                            fontSize: 15,
                          ),
                    ),
                  ],
                ),
              ),
              if (!isSelectionMode) ...[
                // ─── Edit button ───
                if (onEdit != null)
                  GestureDetector(
                    onTap: onEdit,
                    child: Container(
                      padding: const EdgeInsets.all(6),
                      decoration: BoxDecoration(
                        color: isDark
                            ? AppTheme.brand600.withOpacity(0.15)
                            : AppTheme.brand50,
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Icon(
                        Icons.edit_outlined,
                        size: 16,
                        color: AppTheme.brand600.withOpacity(0.7),
                      ),
                    ),
                  ),
                if (onEdit != null) const SizedBox(width: 6),
                // ─── Copy button ───
                GestureDetector(
                  onTap: () {
                    Clipboard.setData(ClipboardData(text: value));
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text('$keyLabel copied to clipboard'),
                        duration: const Duration(seconds: 1),
                      ),
                    );
                  },
                  child: Container(
                    padding: const EdgeInsets.all(6),
                    decoration: BoxDecoration(
                      color: isDark
                          ? const Color(0xFF252839)
                          : AppTheme.neutral100,
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: Icon(
                      Icons.copy_outlined,
                      size: 16,
                      color: Theme.of(context)
                          .colorScheme
                          .onSurface
                          .withOpacity(0.4),
                    ),
                  ),
                ),
                if (onDelete != null) ...[
                  const SizedBox(width: 6),
                  GestureDetector(
                    onTap: onDelete,
                    child: Container(
                      padding: const EdgeInsets.all(6),
                      decoration: BoxDecoration(
                        color: isDark
                            ? const Color(0xFF3A2030)
                            : const Color(0xFFFFF0F0),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Icon(
                        Icons.delete_outline,
                        size: 16,
                        color: const Color(0xFFFA5252).withOpacity(0.7),
                      ),
                    ),
                  ),
                ],
              ],
            ],
          ),
        ),
        if (!isLast)
          Divider(
            height: 1,
            indent: 32,
            color: isDark
                ? const Color(0xFF2D3050)
                : AppTheme.neutral200,
          ),
      ],
    );
  }
}
