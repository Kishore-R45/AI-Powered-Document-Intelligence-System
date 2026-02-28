import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:provider/provider.dart';
import 'package:gap/gap.dart';
import '../../config/theme.dart';
import '../../providers/extracted_data_provider.dart';
import '../../widgets/common/custom_input.dart';
import '../../widgets/common/empty_state.dart';
import '../../widgets/common/animated_list_item.dart';

class ExtractedDataScreen extends StatefulWidget {
  const ExtractedDataScreen({super.key});

  @override
  State<ExtractedDataScreen> createState() => _ExtractedDataScreenState();
}

class _ExtractedDataScreenState extends State<ExtractedDataScreen> {
  final TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<ExtractedDataProvider>().fetchExtractedData();
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;
    final provider = context.watch<ExtractedDataProvider>();
    final grouped = provider.groupedByCategory;

    // Search filter
    final query = _searchController.text.toLowerCase();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Extracted Data'),
      ),
      body: Column(
        children: [
          // Search
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 8, 16, 12),
            child: CustomInput(
              controller: _searchController,
              hint: 'Search extracted data...',
              prefixIcon: Icons.search,
              onChanged: (_) => setState(() {}),
              suffixWidget:
                  _searchController.text.isNotEmpty
                      ? GestureDetector(
                          onTap: () {
                            _searchController.clear();
                            setState(() {});
                          },
                          child: const Icon(Icons.close, size: 20),
                        )
                      : null,
            ),
          ).animate().fadeIn(duration: 300.ms),

          // Data List
          Expanded(
            child: provider.extractedDataList.isEmpty
                ? EmptyState(
                    icon: Icons.table_chart_outlined,
                    title: 'No extracted data',
                    subtitle:
                        'Upload documents to see extracted key-value data',
                  )
                : ListView.builder(
                    padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
                    itemCount: grouped.keys.length,
                    itemBuilder: (context, catIndex) {
                      final category = grouped.keys.toList()[catIndex];
                      final items = grouped[category]!;

                      // Filter items by search
                      final filteredItems = query.isEmpty
                          ? items
                          : items.where((item) {
                              return item.documentName
                                      .toLowerCase()
                                      .contains(query) ||
                                  item.data.entries.any((e) =>
                                      e.key
                                          .toLowerCase()
                                          .contains(query) ||
                                      e.value
                                          .toLowerCase()
                                          .contains(query));
                            }).toList();

                      if (filteredItems.isEmpty) {
                        return const SizedBox.shrink();
                      }

                      return AnimatedListItem(
                        index: catIndex,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            if (catIndex > 0) const Gap(20),

                            // Category Header
                            Row(
                              children: [
                                Container(
                                  width: 4,
                                  height: 20,
                                  decoration: BoxDecoration(
                                    color: _getCategoryColor(category),
                                    borderRadius:
                                        BorderRadius.circular(2),
                                  ),
                                ),
                                const Gap(10),
                                Text(
                                  category,
                                  style: theme.textTheme.titleMedium
                                      ?.copyWith(
                                    fontWeight: FontWeight.w700,
                                  ),
                                ),
                                const Gap(8),
                                Container(
                                  padding: const EdgeInsets.symmetric(
                                      horizontal: 8, vertical: 2),
                                  decoration: BoxDecoration(
                                    color: _getCategoryColor(category)
                                        .withOpacity(0.1),
                                    borderRadius:
                                        BorderRadius.circular(10),
                                  ),
                                  child: Text(
                                    '${filteredItems.length}',
                                    style: TextStyle(
                                      color:
                                          _getCategoryColor(category),
                                      fontWeight: FontWeight.w600,
                                      fontSize: 12,
                                    ),
                                  ),
                                ),
                              ],
                            ),

                            const Gap(12),

                            // Document Cards
                            ...filteredItems.asMap().entries.map((e) {
                              final item = e.value;
                              return Padding(
                                padding:
                                    const EdgeInsets.only(bottom: 10),
                                child: _DocumentDataCard(
                                  documentName: item.documentName,
                                  category: category,
                                  dataCount: item.data.length,
                                  previewKeys: item.data.keys
                                      .take(3)
                                      .toList(),
                                  onTap: () {
                                    Navigator.pushNamed(
                                      context,
                                      '/document-data',
                                      arguments: item,
                                    );
                                  },
                                ),
                              );
                            }),
                          ],
                        ),
                      );
                    },
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
}

class _DocumentDataCard extends StatelessWidget {
  final String documentName;
  final String category;
  final int dataCount;
  final List<String> previewKeys;
  final VoidCallback onTap;

  const _DocumentDataCard({
    required this.documentName,
    required this.category,
    required this.dataCount,
    required this.previewKeys,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(14),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: isDark
              ? Colors.white.withOpacity(0.04)
              : Colors.white,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(
            color: isDark
                ? Colors.white.withOpacity(0.06)
                : Colors.grey.withOpacity(0.1),
          ),
          boxShadow: isDark
              ? null
              : [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.03),
                    blurRadius: 8,
                    offset: const Offset(0, 2),
                  ),
                ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.description_outlined,
                  size: 18,
                  color: theme.colorScheme.onSurface.withOpacity(0.5),
                ),
                const Gap(8),
                Expanded(
                  child: Text(
                    documentName,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: AppTheme.brand600.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    '$dataCount fields',
                    style: const TextStyle(
                      color: AppTheme.brand600,
                      fontWeight: FontWeight.w500,
                      fontSize: 11,
                    ),
                  ),
                ),
              ],
            ),
            if (previewKeys.isNotEmpty) ...[
              const Gap(10),
              Wrap(
                spacing: 6,
                runSpacing: 4,
                children: previewKeys.map((key) {
                  return Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 8, vertical: 3),
                    decoration: BoxDecoration(
                      color: theme.colorScheme.onSurface.withOpacity(0.04),
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: Text(
                      key,
                      style: theme.textTheme.bodySmall?.copyWith(
                        color:
                            theme.colorScheme.onSurface.withOpacity(0.5),
                        fontSize: 11,
                      ),
                    ),
                  );
                }).toList(),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
