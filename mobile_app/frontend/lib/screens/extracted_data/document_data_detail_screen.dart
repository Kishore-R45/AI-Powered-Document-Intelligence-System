import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:gap/gap.dart';
import 'package:provider/provider.dart';
import '../../config/theme.dart';
import '../../models/extracted_data_model.dart';
import '../../providers/extracted_data_provider.dart';
import '../../widgets/common/custom_card.dart';
import '../../widgets/extracted_data/key_value_card.dart';
import '../../widgets/common/animated_list_item.dart';

class DocumentDataDetailScreen extends StatefulWidget {
  final ExtractedDataModel extractedData;

  const DocumentDataDetailScreen({super.key, required this.extractedData});

  @override
  State<DocumentDataDetailScreen> createState() => _DocumentDataDetailScreenState();
}

class _DocumentDataDetailScreenState extends State<DocumentDataDetailScreen> {
  late ExtractedDataModel _currentData;
  bool _isEditMode = false;
  final Set<String> _selectedKeys = {};

  @override
  void initState() {
    super.initState();
    _currentData = widget.extractedData;
  }

  void _toggleEditMode() {
    setState(() {
      _isEditMode = !_isEditMode;
      if (!_isEditMode) _selectedKeys.clear();
    });
  }

  void _toggleSelection(String key) {
    setState(() {
      if (_selectedKeys.contains(key)) {
        _selectedKeys.remove(key);
      } else {
        _selectedKeys.add(key);
      }
    });
  }

  void _selectAll() {
    setState(() {
      if (_selectedKeys.length == _currentData.data.length) {
        _selectedKeys.clear();
      } else {
        _selectedKeys.addAll(_currentData.data.keys);
      }
    });
  }

  // ─── Edit a single field ───
  Future<void> _editField(String key, String currentValue) async {
    final controller = TextEditingController(text: currentValue);
    final result = await showDialog<String>(
      context: context,
      builder: (ctx) {
        final isDark = Theme.of(ctx).brightness == Brightness.dark;
        return AlertDialog(
          title: Text('Edit "$key"'),
          content: TextField(
            controller: controller,
            maxLines: 3,
            decoration: InputDecoration(
              labelText: 'Value',
              hintText: 'Enter new value',
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(10),
              ),
              filled: true,
              fillColor: isDark ? const Color(0xFF1E2035) : AppTheme.neutral50,
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: const Text('Cancel'),
            ),
            FilledButton(
              onPressed: () => Navigator.pop(ctx, controller.text.trim()),
              child: const Text('Save'),
            ),
          ],
        );
      },
    );

    if (result == null || result.isEmpty || result == currentValue || !mounted) return;

    final provider = context.read<ExtractedDataProvider>();
    final success = await provider.updateField(_currentData.documentId, key, result);

    if (!mounted) return;

    if (success) {
      setState(() {
        final updatedData = Map<String, String>.from(_currentData.data);
        updatedData[key] = result;
        _currentData = _currentData.copyWith(data: updatedData);
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('"$key" updated'),
          backgroundColor: const Color(0xFF20C997),
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        ),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('Failed to update field'),
          backgroundColor: const Color(0xFFFA5252),
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        ),
      );
    }
  }

  // ─── Delete a single field ───
  Future<void> _deleteField(String key) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Delete Field'),
        content: Text('Are you sure you want to delete "$key"?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(ctx, true),
            style: TextButton.styleFrom(foregroundColor: const Color(0xFFFA5252)),
            child: const Text('Delete'),
          ),
        ],
      ),
    );

    if (confirmed != true || !mounted) return;

    final provider = context.read<ExtractedDataProvider>();
    final success = await provider.deleteField(_currentData.documentId, key);

    if (!mounted) return;

    if (success) {
      setState(() {
        final updatedData = Map<String, String>.from(_currentData.data);
        updatedData.remove(key);
        _currentData = _currentData.copyWith(data: updatedData);
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('"$key" deleted'),
          backgroundColor: const Color(0xFF20C997),
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        ),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('Failed to delete field'),
          backgroundColor: const Color(0xFFFA5252),
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        ),
      );
    }
  }

  // ─── Delete selected fields ───
  Future<void> _deleteSelected() async {
    if (_selectedKeys.isEmpty) return;

    final count = _selectedKeys.length;
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Delete Selected'),
        content: Text('Are you sure you want to delete $count selected field(s)?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(ctx, true),
            style: TextButton.styleFrom(foregroundColor: const Color(0xFFFA5252)),
            child: const Text('Delete'),
          ),
        ],
      ),
    );

    if (confirmed != true || !mounted) return;

    final provider = context.read<ExtractedDataProvider>();
    final keysToDelete = _selectedKeys.toList();
    final success = await provider.deleteFields(_currentData.documentId, keysToDelete);

    if (!mounted) return;

    if (success) {
      setState(() {
        final updatedData = Map<String, String>.from(_currentData.data);
        for (final key in keysToDelete) {
          updatedData.remove(key);
        }
        _currentData = _currentData.copyWith(data: updatedData);
        _selectedKeys.clear();
        if (updatedData.isEmpty) _isEditMode = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('$count field(s) deleted'),
          backgroundColor: const Color(0xFF20C997),
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        ),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('Failed to delete selected fields'),
          backgroundColor: const Color(0xFFFA5252),
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;
    final entries = _currentData.data.entries.toList();

    return Scaffold(
      appBar: AppBar(
        leading: _isEditMode
            ? IconButton(
                onPressed: _toggleEditMode,
                icon: const Icon(Icons.close),
                tooltip: 'Cancel',
              )
            : null,
        title: _isEditMode
            ? Text(
                '${_selectedKeys.length} selected',
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w700,
                ),
              )
            : Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    _currentData.documentName,
                    style: theme.textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  Text(
                    '${entries.length} extracted fields',
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: theme.colorScheme.onSurface.withOpacity(0.5),
                    ),
                  ),
                ],
              ),
        actions: _isEditMode
            ? [
                // Select all checkbox
                IconButton(
                  onPressed: _selectAll,
                  icon: Icon(
                    _selectedKeys.length == entries.length
                        ? Icons.deselect
                        : Icons.select_all,
                    size: 22,
                  ),
                  tooltip: _selectedKeys.length == entries.length
                      ? 'Deselect all'
                      : 'Select all',
                ),
                // Delete selected
                IconButton(
                  onPressed: _selectedKeys.isEmpty ? null : _deleteSelected,
                  icon: Icon(
                    Icons.delete_outlined,
                    size: 22,
                    color: _selectedKeys.isEmpty
                        ? theme.colorScheme.onSurface.withOpacity(0.3)
                        : const Color(0xFFFA5252),
                  ),
                  tooltip: 'Delete selected',
                ),
                const SizedBox(width: 4),
              ]
            : [
                // Global edit mode button
                if (entries.isNotEmpty)
                  IconButton(
                    onPressed: _toggleEditMode,
                    icon: const Icon(Icons.checklist, size: 22),
                    tooltip: 'Select & manage fields',
                  ),
                IconButton(
                  onPressed: () => _copyAll(context),
                  icon: const Icon(Icons.copy_all, size: 22),
                  tooltip: 'Copy all data',
                ),
                const SizedBox(width: 4),
              ],
      ),
      body: entries.isEmpty
          ? Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.table_chart_outlined,
                    size: 64,
                    color: theme.colorScheme.onSurface.withOpacity(0.15),
                  ),
                  const Gap(16),
                  Text(
                    'No data extracted',
                    style: theme.textTheme.titleMedium?.copyWith(
                      color: theme.colorScheme.onSurface.withOpacity(0.4),
                    ),
                  ),
                ],
              ),
            )
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                // ─── Header Card ───
                if (!_isEditMode)
                  CustomCard(
                    gradient: LinearGradient(
                      colors: isDark
                          ? [
                              AppTheme.brand400.withOpacity(0.08),
                              AppTheme.brand400.withOpacity(0.03),
                            ]
                          : [
                              AppTheme.brand50,
                              AppTheme.brand50.withOpacity(0.3),
                            ],
                    ),
                    padding: const EdgeInsets.all(16),
                    child: Row(
                      children: [
                        Container(
                          width: 48,
                          height: 48,
                          decoration: BoxDecoration(
                            color: AppTheme.brand600.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(14),
                          ),
                          child: const Icon(
                            Icons.table_chart,
                            color: AppTheme.brand600,
                            size: 24,
                          ),
                        ),
                        const Gap(16),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Extracted Key-Value Pairs',
                                style: theme.textTheme.titleSmall?.copyWith(
                                  fontWeight: FontWeight.w700,
                                ),
                              ),
                              const Gap(2),
                              Text(
                                'Data available offline',
                                style: theme.textTheme.bodySmall?.copyWith(
                                  color: const Color(0xFF20C997),
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                            ],
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(
                            color: AppTheme.brand600.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              const Icon(Icons.offline_bolt,
                                  size: 14, color: Color(0xFF20C997)),
                              const Gap(4),
                              Text(
                                'Offline',
                                style: TextStyle(
                                  color: const Color(0xFF20C997),
                                  fontWeight: FontWeight.w600,
                                  fontSize: 11,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ).animate().fadeIn(duration: 400.ms),

                if (!_isEditMode) const Gap(20),

                // ─── Edit mode hint ───
                if (_isEditMode)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 12),
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                      decoration: BoxDecoration(
                        color: isDark
                            ? AppTheme.brand600.withOpacity(0.1)
                            : AppTheme.brand50,
                        borderRadius: BorderRadius.circular(10),
                        border: Border.all(
                          color: AppTheme.brand600.withOpacity(0.2),
                        ),
                      ),
                      child: Row(
                        children: [
                          Icon(Icons.info_outline, size: 18, color: AppTheme.brand600),
                          const SizedBox(width: 10),
                          Expanded(
                            child: Text(
                              'Select fields to delete them. Tap the select all icon to toggle all.',
                              style: theme.textTheme.bodySmall?.copyWith(
                                color: AppTheme.brand600,
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),

                // ─── Key-Value Pairs ───
                ...entries.asMap().entries.map((entry) {
                  final i = entry.key;
                  final kv = entry.value;

                  return AnimatedListItem(
                    index: i,
                    child: Padding(
                      padding: const EdgeInsets.only(bottom: 10),
                      child: KeyValueCard(
                        keyLabel: kv.key,
                        value: kv.value,
                        isSelectionMode: _isEditMode,
                        isSelected: _selectedKeys.contains(kv.key),
                        onSelectionChanged: (_) => _toggleSelection(kv.key),
                        onEdit: _isEditMode ? null : () => _editField(kv.key, kv.value),
                        onDelete: _isEditMode ? null : () => _deleteField(kv.key),
                      ),
                    ),
                  );
                }),

                const Gap(16),
              ],
            ),
    );
  }

  Color _getFieldColor(int index) {
    final colors = [
      AppTheme.brand600,
      const Color(0xFF7C4DFF),
      const Color(0xFF20C997),
      const Color(0xFFF59F00),
      const Color(0xFFE64980),
      const Color(0xFF339AF0),
    ];
    return colors[index % colors.length];
  }

  void _copyAll(BuildContext context) {
    final buffer = StringBuffer();
    for (final entry in _currentData.data.entries) {
      buffer.writeln('${entry.key}: ${entry.value}');
    }
    Clipboard.setData(ClipboardData(text: buffer.toString()));

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: const Text('All data copied to clipboard'),
        backgroundColor: AppTheme.brand600,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      ),
    );
  }
}
