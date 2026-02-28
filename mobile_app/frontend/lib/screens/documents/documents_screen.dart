import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:provider/provider.dart';
import 'package:gap/gap.dart';
import '../../config/theme.dart';
import '../../config/constants.dart';
import '../../providers/document_provider.dart';
import '../../widgets/documents/document_card.dart';
import '../../widgets/common/empty_state.dart';
import '../../widgets/common/custom_input.dart';

class DocumentsScreen extends StatefulWidget {
  const DocumentsScreen({super.key});

  @override
  State<DocumentsScreen> createState() => _DocumentsScreenState();
}

class _DocumentsScreenState extends State<DocumentsScreen> {
  bool _isGridView = true;
  String _selectedCategory = 'All';
  final TextEditingController _searchController = TextEditingController();

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;
    final docProvider = context.watch<DocumentProvider>();

    // Filter documents
    var docs = docProvider.documents;
    if (_selectedCategory != 'All') {
      docs = docs.where((d) => d.category == _selectedCategory).toList();
    }
    if (_searchController.text.isNotEmpty) {
      final q = _searchController.text.toLowerCase();
      docs = docs
          .where((d) =>
              d.name.toLowerCase().contains(q) ||
              d.category.toLowerCase().contains(q))
          .toList();
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('My Documents'),
        automaticallyImplyLeading: false,
        actions: [
          IconButton(
            onPressed: () {
              setState(() => _isGridView = !_isGridView);
            },
            icon: Icon(
              _isGridView ? Icons.view_list_rounded : Icons.grid_view_rounded,
              size: 22,
            ),
          ),
          const SizedBox(width: 4),
        ],
      ),
      body: Column(
        children: [
          // ─── Search Bar ───
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 8, 16, 0),
            child: CustomInput(
              controller: _searchController,
              hint: 'Search documents...',
              prefixIcon: Icons.search,
              onChanged: (_) => setState(() {}),
              suffixWidget: _searchController.text.isNotEmpty
                  ? GestureDetector(
                      onTap: () {
                        _searchController.clear();
                        setState(() {});
                      },
                      child: const Icon(Icons.close, size: 20),
                    )
                  : null,
            ),
          ).animate().fadeIn(duration: 300.ms).slideY(begin: -0.1),

          const Gap(12),

          // ─── Category Filter Chips ───
          SizedBox(
            height: 40,
            child: ListView(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: 16),
              children: AppConstants.documentCategories.map((cat) {
                final isSelected = _selectedCategory == cat;
                return Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: FilterChip(
                    label: Text(cat),
                    selected: isSelected,
                    onSelected: (_) =>
                        setState(() => _selectedCategory = cat),
                    selectedColor: isDark
                        ? AppTheme.brand400.withOpacity(0.2)
                        : AppTheme.brand50,
                    checkmarkColor: AppTheme.brand600,
                    labelStyle: TextStyle(
                      color: isSelected
                          ? AppTheme.brand600
                          : theme.colorScheme.onSurface.withOpacity(0.6),
                      fontWeight:
                          isSelected ? FontWeight.w600 : FontWeight.w400,
                      fontSize: 13,
                    ),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(20),
                    ),
                    side: BorderSide(
                      color: isSelected
                          ? AppTheme.brand600.withOpacity(0.3)
                          : theme.colorScheme.onSurface.withOpacity(0.1),
                    ),
                  ),
                );
              }).toList(),
            ),
          ).animate().fadeIn(delay: 100.ms, duration: 300.ms),

          const Gap(12),

          // ─── Results Count ───
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Row(
              children: [
                Text(
                  '${docs.length} document${docs.length != 1 ? 's' : ''}',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurface.withOpacity(0.5),
                  ),
                ),
                const Spacer(),
                Text(
                  _selectedCategory != 'All' ? _selectedCategory : '',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: AppTheme.brand600,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),

          const Gap(8),

          // ─── Documents List / Grid ───
          Expanded(
            child: docs.isEmpty
                ? EmptyState(
                    icon: Icons.description_outlined,
                    title: 'No documents found',
                    subtitle: _searchController.text.isNotEmpty
                        ? 'Try a different search term'
                        : 'Upload your first document to get started',
                    actionText: 'Upload Document',
                    onAction: () =>
                        Navigator.pushNamed(context, '/upload'),
                  )
                : _isGridView
                    ? _buildGrid(docs)
                    : _buildList(docs),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _showUploadOptions(context),
        backgroundColor: AppTheme.brand600,
        foregroundColor: Colors.white,
        icon: const Icon(Icons.add_rounded),
        label: const Text('Add'),
      )
          .animate()
          .fadeIn(delay: 500.ms, duration: 300.ms)
          .scale(begin: const Offset(0.8, 0.8)),
    );
  }

  Widget _buildGrid(List docs) {
    return GridView.builder(
      padding: const EdgeInsets.fromLTRB(16, 0, 16, 80),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        mainAxisSpacing: 12,
        crossAxisSpacing: 12,
        childAspectRatio: 0.78,
      ),
      itemCount: docs.length,
      itemBuilder: (context, index) {
        return DocumentCard(
          document: docs[index],
          isGridView: true,
          onTap: () => Navigator.pushNamed(
            context,
            '/document-viewer',
            arguments: docs[index],
          ),
        )
            .animate()
            .fadeIn(
                delay: Duration(milliseconds: 50 * index), duration: 300.ms)
            .scale(
                begin: const Offset(0.95, 0.95),
                duration: 300.ms,
                curve: Curves.easeOut);
      },
    );
  }

  Widget _buildList(List docs) {
    return ListView.builder(
      padding: const EdgeInsets.fromLTRB(16, 0, 16, 80),
      itemCount: docs.length,
      itemBuilder: (context, index) {
        return Padding(
          padding: const EdgeInsets.only(bottom: 10),
          child: DocumentCard(
            document: docs[index],
            isGridView: false,
            onTap: () => Navigator.pushNamed(
              context,
              '/document-viewer',
              arguments: docs[index],
            ),
          )
              .animate()
              .fadeIn(
                  delay: Duration(milliseconds: 50 * index),
                  duration: 300.ms)
              .slideX(begin: 0.05, duration: 300.ms),
        );
      },
    );
  }

  void _showUploadOptions(BuildContext context) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: Colors.grey.withOpacity(0.3),
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
              const Gap(20),
              Text(
                'Add Document',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
              ),
              const Gap(24),
              _UploadOption(
                icon: Icons.camera_alt_outlined,
                label: 'Scan Document',
                subtitle: 'Use camera to scan',
                color: AppTheme.brand600,
                onTap: () {
                  Navigator.pop(ctx);
                  Navigator.pushNamed(context, '/scan');
                },
              ),
              const Gap(12),
              _UploadOption(
                icon: Icons.upload_file_outlined,
                label: 'Upload File',
                subtitle: 'Choose from files',
                color: const Color(0xFF7C4DFF),
                onTap: () {
                  Navigator.pop(ctx);
                  Navigator.pushNamed(context, '/upload');
                },
              ),
              const Gap(12),
              _UploadOption(
                icon: Icons.photo_library_outlined,
                label: 'From Gallery',
                subtitle: 'Select from photos',
                color: const Color(0xFF20C997),
                onTap: () {
                  Navigator.pop(ctx);
                  Navigator.pushNamed(context, '/upload');
                },
              ),
              const Gap(16),
            ],
          ),
        ),
      ),
    );
  }
}

class _UploadOption extends StatelessWidget {
  final IconData icon;
  final String label;
  final String subtitle;
  final Color color;
  final VoidCallback onTap;

  const _UploadOption({
    required this.icon,
    required this.label,
    required this.subtitle,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: isDark ? color.withOpacity(0.08) : color.withOpacity(0.05),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: color.withOpacity(0.15)),
        ),
        child: Row(
          children: [
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(14),
              ),
              child: Icon(icon, color: color, size: 24),
            ),
            const Gap(16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    label,
                    style: theme.textTheme.bodyLarge?.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  Text(
                    subtitle,
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: theme.colorScheme.onSurface.withOpacity(0.5),
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
      ),
    );
  }
}
