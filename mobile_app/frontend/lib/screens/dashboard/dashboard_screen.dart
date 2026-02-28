import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:provider/provider.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:gap/gap.dart';
import '../../config/theme.dart';
import '../../config/constants.dart';
import '../../providers/document_provider.dart';
import '../../providers/auth_provider.dart';
import '../../widgets/common/custom_card.dart';
import '../../widgets/common/animated_list_item.dart';

class DashboardScreen extends StatelessWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;
    final docProvider = context.watch<DocumentProvider>();
    final auth = context.watch<AuthProvider>();

    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Welcome back,',
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurface.withOpacity(0.5),
              ),
            ),
            Text(
              auth.user?.name ?? 'User',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w700,
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            onPressed: () => Navigator.pushNamed(context, '/profile'),
            icon: CircleAvatar(
              radius: 18,
              backgroundColor: AppTheme.brand100,
              child: Text(
                auth.user?.initials ?? 'U',
                style: const TextStyle(
                  color: AppTheme.brand700,
                  fontWeight: FontWeight.w600,
                  fontSize: 14,
                ),
              ),
            ),
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: RefreshIndicator(
        color: AppTheme.brand600,
        onRefresh: () async {
          await docProvider.fetchDocuments();
        },
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // ─── Summary Cards ───
            _buildSummaryCards(context, docProvider),
            const Gap(24),

            // ─── Category Breakdown Chart ───
            AnimatedListItem(
              index: 1,
              child: _buildCategoryChart(context, docProvider),
            ),
            const Gap(24),

            // ─── Quick Actions ───
            AnimatedListItem(
              index: 2,
              child: _buildQuickActions(context),
            ),
            const Gap(24),

            // ─── Recent Activity ───
            AnimatedListItem(
              index: 3,
              child: _buildRecentActivity(context, docProvider),
            ),
            const Gap(24),

            // ─── Expiring Soon ───
            AnimatedListItem(
              index: 4,
              child: _buildExpiringSoon(context, docProvider),
            ),
            const Gap(16),
          ],
        ),
      ),
    );
  }

  Widget _buildSummaryCards(BuildContext context, DocumentProvider provider) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;
    final total = provider.documents.length;
    final expiring = provider.documents
        .where((d) =>
            d.expiryDate != null &&
            d.expiryDate!.difference(DateTime.now()).inDays <= 30 &&
            d.expiryDate!.isAfter(DateTime.now()))
        .length;
    final expired = provider.documents
        .where((d) =>
            d.expiryDate != null && d.expiryDate!.isBefore(DateTime.now()))
        .length;
    final categories = provider.documents.map((d) => d.category).toSet().length;

    final cards = [
      _SummaryData(
        'Total Docs',
        total.toString(),
        Icons.description_outlined,
        AppTheme.brand600,
        AppTheme.brand50,
      ),
      _SummaryData(
        'Expiring Soon',
        expiring.toString(),
        Icons.schedule_outlined,
        const Color(0xFFF59F00),
        const Color(0xFFFFF9DB),
      ),
      _SummaryData(
        'Expired',
        expired.toString(),
        Icons.warning_amber_rounded,
        const Color(0xFFFA5252),
        const Color(0xFFFFF5F5),
      ),
      _SummaryData(
        'Categories',
        categories.toString(),
        Icons.category_outlined,
        const Color(0xFF20C997),
        const Color(0xFFE6FCF5),
      ),
    ];

    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        mainAxisSpacing: 12,
        crossAxisSpacing: 12,
        childAspectRatio: 1.55,
      ),
      itemCount: cards.length,
      itemBuilder: (c, i) {
        final data = cards[i];
        return AnimatedListItem(
          index: i,
          child: CustomCard(
            padding: const EdgeInsets.all(14),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: isDark
                        ? data.color.withOpacity(0.15)
                        : data.bgColor,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(data.icon, color: data.color, size: 26),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        data.label,
                        style: theme.textTheme.bodyMedium?.copyWith(
                          color:
                              theme.colorScheme.onSurface.withOpacity(0.55),
                          fontSize: 13,
                          fontWeight: FontWeight.w500,
                        ),
                        overflow: TextOverflow.ellipsis,
                        maxLines: 1,
                      ),
                      const SizedBox(height: 4),
                      Text(
                        data.value,
                        style: theme.textTheme.headlineSmall?.copyWith(
                          fontWeight: FontWeight.w800,
                          fontSize: 24,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildCategoryChart(
      BuildContext context, DocumentProvider provider) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    final categoryMap = <String, int>{};
    for (final doc in provider.documents) {
      categoryMap[doc.category] = (categoryMap[doc.category] ?? 0) + 1;
    }

    final colors = [
      AppTheme.brand600,
      const Color(0xFF7C4DFF),
      const Color(0xFF20C997),
      const Color(0xFFFF6B6B),
      const Color(0xFFF59F00),
      const Color(0xFF339AF0),
    ];

    int colorIndex = 0;
    final sections = categoryMap.entries.map((e) {
      final color = colors[colorIndex % colors.length];
      colorIndex++;
      return PieChartSectionData(
        value: e.value.toDouble(),
        title: '${e.value}',
        color: color,
        radius: 24,
        titleStyle: const TextStyle(
          color: Colors.white,
          fontWeight: FontWeight.bold,
          fontSize: 12,
        ),
      );
    }).toList();

    return CustomCard(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Documents by Category',
            style: theme.textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.w700,
            ),
          ),
          const Gap(20),
          Row(
            children: [
              SizedBox(
                width: 100,
                height: 100,
                child: PieChart(
                  PieChartData(
                    sections: sections,
                    centerSpaceRadius: 25,
                    sectionsSpace: 2,
                  ),
                ),
              ),
              const Gap(24),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    ...categoryMap.entries.toList().asMap().entries.map((e) {
                      final color = colors[e.key % colors.length];
                      return Padding(
                        padding: const EdgeInsets.only(bottom: 8),
                        child: Row(
                          children: [
                            Container(
                              width: 10,
                              height: 10,
                              decoration: BoxDecoration(
                                color: color,
                                borderRadius: BorderRadius.circular(3),
                              ),
                            ),
                            const Gap(8),
                            Expanded(
                              child: Text(
                                e.value.key,
                                style: theme.textTheme.bodySmall,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                            Text(
                              '${e.value.value}',
                              style: theme.textTheme.bodySmall?.copyWith(
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ],
                        ),
                      );
                    }),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildQuickActions(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    final actions = [
      _QuickAction(
        'Scan',
        Icons.camera_alt_outlined,
        AppTheme.brand600,
        () => Navigator.pushNamed(context, '/scan'),
      ),
      _QuickAction(
        'Upload',
        Icons.upload_file_outlined,
        const Color(0xFF7C4DFF),
        () => Navigator.pushNamed(context, '/upload'),
      ),
      _QuickAction(
        'AI Chat',
        Icons.smart_toy_outlined,
        const Color(0xFF20C997),
        () {}, // handled by bottom nav
      ),
      _QuickAction(
        'Data',
        Icons.table_chart_outlined,
        const Color(0xFFF59F00),
        () => Navigator.pushNamed(context, '/extracted-data'),
      ),
    ];

    return CustomCard(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Quick Actions',
            style: theme.textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.w700,
            ),
          ),
          const Gap(16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: actions.map((action) {
              return GestureDetector(
                onTap: action.onTap,
                child: Column(
                  children: [
                    Container(
                      width: 56,
                      height: 56,
                      decoration: BoxDecoration(
                        color: isDark
                            ? action.color.withOpacity(0.15)
                            : action.color.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(16),
                      ),
                      child: Icon(action.icon, color: action.color, size: 26),
                    ),
                    const Gap(8),
                    Text(
                      action.label,
                      style: theme.textTheme.bodySmall?.copyWith(
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              )
                  .animate()
                  .fadeIn(
                      delay: Duration(
                          milliseconds: 100 * actions.indexOf(action)),
                      duration: 300.ms)
                  .scale(
                      begin: const Offset(0.8, 0.8),
                      end: const Offset(1, 1),
                      duration: 300.ms);
            }).toList(),
          ),
        ],
      ),
    );
  }

  Widget _buildRecentActivity(
      BuildContext context, DocumentProvider provider) {
    final theme = Theme.of(context);
    final recentDocs = provider.documents.take(4).toList();

    return CustomCard(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Recent Documents',
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w700,
                ),
              ),
              TextButton(
                onPressed: () {},
                child: const Text('View All'),
              ),
            ],
          ),
          if (recentDocs.isEmpty)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 24),
              child: Center(
                child: Text(
                  'No documents yet',
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: theme.colorScheme.onSurface.withOpacity(0.5),
                  ),
                ),
              ),
            )
          else
            ...recentDocs.asMap().entries.map((e) {
              final doc = e.value;
              final categoryIcon = _getCategoryIcon(doc.category);
              final categoryColor = _getCategoryColor(doc.category);

              return ListTile(
                contentPadding: EdgeInsets.zero,
                leading: Container(
                  width: 42,
                  height: 42,
                  decoration: BoxDecoration(
                    color: categoryColor.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child:
                      Icon(categoryIcon, color: categoryColor, size: 20),
                ),
                title: Text(
                  doc.name,
                  style: theme.textTheme.bodyMedium?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                subtitle: Text(
                  doc.category,
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurface.withOpacity(0.5),
                  ),
                ),
                trailing: Text(
                  _formatDate(doc.uploadDate),
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurface.withOpacity(0.4),
                    fontSize: 11,
                  ),
                ),
              );
            }),
        ],
      ),
    );
  }

  Widget _buildExpiringSoon(
      BuildContext context, DocumentProvider provider) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;
    final expiring = provider.documents
        .where((d) =>
            d.expiryDate != null &&
            d.expiryDate!.difference(DateTime.now()).inDays <= 90 &&
            d.expiryDate!.isAfter(DateTime.now()))
        .toList()
      ..sort((a, b) => a.expiryDate!.compareTo(b.expiryDate!));

    if (expiring.isEmpty) return const SizedBox.shrink();

    return CustomCard(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.schedule,
                size: 20,
                color: const Color(0xFFF59F00),
              ),
              const Gap(8),
              Text(
                'Expiring Soon',
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w700,
                ),
              ),
            ],
          ),
          const Gap(16),
          ...expiring.take(3).map((doc) {
            final daysLeft =
                doc.expiryDate!.difference(DateTime.now()).inDays;
            final urgency = daysLeft <= 7
                ? const Color(0xFFFA5252)
                : daysLeft <= 30
                    ? const Color(0xFFF59F00)
                    : const Color(0xFF20C997);

            return Container(
              margin: const EdgeInsets.only(bottom: 10),
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: isDark
                    ? urgency.withOpacity(0.08)
                    : urgency.withOpacity(0.05),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: urgency.withOpacity(0.2),
                ),
              ),
              child: Row(
                children: [
                  Container(
                    width: 4,
                    height: 40,
                    decoration: BoxDecoration(
                      color: urgency,
                      borderRadius: BorderRadius.circular(2),
                    ),
                  ),
                  const Gap(12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          doc.name,
                          style: theme.textTheme.bodyMedium?.copyWith(
                            fontWeight: FontWeight.w600,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                        Text(
                          'Expires in $daysLeft days',
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: urgency,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                  ),
                  Icon(
                    Icons.chevron_right,
                    color: theme.colorScheme.onSurface.withOpacity(0.3),
                  ),
                ],
              ),
            );
          }),
        ],
      ),
    );
  }

  IconData _getCategoryIcon(String category) {
    switch (category.toLowerCase()) {
      case 'identity':
        return Icons.badge_outlined;
      case 'education':
        return Icons.school_outlined;
      case 'finance':
        return Icons.account_balance_outlined;
      case 'insurance':
        return Icons.health_and_safety_outlined;
      case 'medical':
        return Icons.local_hospital_outlined;
      case 'legal':
        return Icons.gavel_outlined;
      default:
        return Icons.description_outlined;
    }
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

  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final diff = now.difference(date);
    if (diff.inDays == 0) return 'Today';
    if (diff.inDays == 1) return 'Yesterday';
    if (diff.inDays < 7) return '${diff.inDays}d ago';
    return '${date.day}/${date.month}/${date.year}';
  }
}

class _SummaryData {
  final String label;
  final String value;
  final IconData icon;
  final Color color;
  final Color bgColor;

  _SummaryData(this.label, this.value, this.icon, this.color, this.bgColor);
}

class _QuickAction {
  final String label;
  final IconData icon;
  final Color color;
  final VoidCallback onTap;

  _QuickAction(this.label, this.icon, this.color, this.onTap);
}
