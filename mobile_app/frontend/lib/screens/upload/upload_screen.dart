import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:file_picker/file_picker.dart';
import 'package:provider/provider.dart';
import 'package:gap/gap.dart';
import '../../config/theme.dart';
import '../../config/constants.dart';
import '../../providers/document_provider.dart';
import '../../widgets/common/custom_button.dart';
import '../../widgets/common/custom_input.dart';
import '../../widgets/common/custom_card.dart';

class UploadScreen extends StatefulWidget {
  const UploadScreen({super.key});

  @override
  State<UploadScreen> createState() => _UploadScreenState();
}

class _UploadScreenState extends State<UploadScreen> {
  String? _selectedCategory;
  File? _selectedFile;
  String? _selectedFileName;
  bool _isUploading = false;
  final TextEditingController _nameController = TextEditingController();
  DateTime? _expiryDate;

  @override
  void dispose() {
    _nameController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Upload Document'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // ─── File Picker Area ───
            _buildFilePicker(context)
                .animate()
                .fadeIn(duration: 400.ms)
                .slideY(begin: 0.05),

            const Gap(24),

            // ─── Document Name ───
            Text(
              'Document Name',
              style: theme.textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
            const Gap(8),
            CustomInput(
              controller: _nameController,
              hint: 'Enter document name',
              prefixIcon: Icons.description_outlined,
            ).animate().fadeIn(delay: 100.ms, duration: 400.ms),

            const Gap(20),

            // ─── Category Selector ───
            Text(
              'Category',
              style: theme.textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
            const Gap(8),
            _buildCategorySelector(context)
                .animate()
                .fadeIn(delay: 200.ms, duration: 400.ms),

            const Gap(20),

            // ─── Expiry Date ───
            Text(
              'Expiry Date (Optional)',
              style: theme.textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
            const Gap(8),
            _buildDatePicker(context)
                .animate()
                .fadeIn(delay: 300.ms, duration: 400.ms),

            const Gap(32),

            // ─── Upload Progress ───
            if (_isUploading) ...[
              _buildUploadProgress(context),
              const Gap(24),
            ],

            // ─── Upload Button ───
            CustomButton(
              text: _isUploading ? 'Uploading...' : 'Upload Document',
              leftIcon: Icons.cloud_upload_outlined,
              isLoading: _isUploading,
              onPressed: _selectedFile != null && !_isUploading
                  ? _handleUpload
                  : null,
              fullWidth: true,
            ).animate().fadeIn(delay: 400.ms, duration: 400.ms),

            const Gap(20),
          ],
        ),
      ),
    );
  }

  Widget _buildFilePicker(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return GestureDetector(
      onTap: _pickFile,
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(vertical: 40),
        decoration: BoxDecoration(
          color: isDark
              ? AppTheme.brand400.withOpacity(0.05)
              : AppTheme.brand50.withOpacity(0.5),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: _selectedFileName != null
                ? AppTheme.brand600.withOpacity(0.3)
                : (isDark
                    ? Colors.white.withOpacity(0.08)
                    : Colors.grey.withOpacity(0.2)),
            width: 2,
            style: BorderStyle.solid,
          ),
        ),
        child: _selectedFileName != null
            ? Column(
                children: [
                  Container(
                    width: 56,
                    height: 56,
                    decoration: BoxDecoration(
                      color: AppTheme.brand600.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(14),
                    ),
                    child: const Icon(
                      Icons.picture_as_pdf,
                      color: AppTheme.brand600,
                      size: 28,
                    ),
                  ),
                  const Gap(12),
                  Text(
                    _selectedFileName!,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const Gap(4),
                  Text(
                    'Tap to change',
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: AppTheme.brand600,
                    ),
                  ),
                ],
              )
            : Column(
                children: [
                  Container(
                    width: 64,
                    height: 64,
                    decoration: BoxDecoration(
                      color: isDark
                          ? Colors.white.withOpacity(0.05)
                          : AppTheme.brand50,
                      shape: BoxShape.circle,
                    ),
                    child: Icon(
                      Icons.cloud_upload_outlined,
                      size: 30,
                      color: AppTheme.brand600.withOpacity(0.6),
                    ),
                  ),
                  const Gap(16),
                  Text(
                    'Tap to select a file',
                    style: theme.textTheme.bodyLarge?.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const Gap(4),
                  Text(
                    'PDF, JPG, PNG up to 10MB',
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: theme.colorScheme.onSurface.withOpacity(0.5),
                    ),
                  ),
                ],
              ),
      ),
    );
  }

  Widget _buildCategorySelector(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: AppConstants.documentCategories.map((cat) {
        final isSelected = _selectedCategory == cat;
        return GestureDetector(
          onTap: () => setState(() => _selectedCategory = cat),
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 200),
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
            decoration: BoxDecoration(
              color: isSelected
                  ? AppTheme.brand600
                  : (isDark
                      ? Colors.white.withOpacity(0.05)
                      : Colors.grey.withOpacity(0.08)),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: isSelected
                    ? AppTheme.brand600
                    : (isDark
                        ? Colors.white.withOpacity(0.08)
                        : Colors.grey.withOpacity(0.15)),
              ),
            ),
            child: Text(
              cat,
              style: TextStyle(
                color: isSelected
                    ? Colors.white
                    : theme.colorScheme.onSurface.withOpacity(0.7),
                fontWeight: isSelected ? FontWeight.w600 : FontWeight.w400,
                fontSize: 13,
              ),
            ),
          ),
        );
      }).toList(),
    );
  }

  Widget _buildDatePicker(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return GestureDetector(
      onTap: () async {
        final date = await showDatePicker(
          context: context,
          initialDate: DateTime.now().add(const Duration(days: 365)),
          firstDate: DateTime.now(),
          lastDate: DateTime.now().add(const Duration(days: 3650)),
        );
        if (date != null) {
          setState(() => _expiryDate = date);
        }
      },
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        decoration: BoxDecoration(
          color: isDark
              ? Colors.white.withOpacity(0.05)
              : Colors.grey.withOpacity(0.06),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isDark
                ? Colors.white.withOpacity(0.08)
                : Colors.grey.withOpacity(0.15),
          ),
        ),
        child: Row(
          children: [
            Icon(
              Icons.calendar_today_outlined,
              size: 20,
              color: theme.colorScheme.onSurface.withOpacity(0.4),
            ),
            const Gap(12),
            Text(
              _expiryDate != null
                  ? '${_expiryDate!.day}/${_expiryDate!.month}/${_expiryDate!.year}'
                  : 'Select expiry date',
              style: theme.textTheme.bodyMedium?.copyWith(
                color: _expiryDate != null
                    ? null
                    : theme.colorScheme.onSurface.withOpacity(0.4),
              ),
            ),
            const Spacer(),
            if (_expiryDate != null)
              GestureDetector(
                onTap: () => setState(() => _expiryDate = null),
                child: Icon(
                  Icons.close,
                  size: 18,
                  color: theme.colorScheme.onSurface.withOpacity(0.4),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildUploadProgress(BuildContext context) {
    final theme = Theme.of(context);

    return CustomCard(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.cloud_upload_outlined,
                  color: AppTheme.brand600, size: 20),
              const Gap(8),
              Text(
                'Uploading...',
                style: theme.textTheme.bodyMedium?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          const Gap(12),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: const LinearProgressIndicator(
              minHeight: 6,
              backgroundColor: AppTheme.brand100,
              valueColor: AlwaysStoppedAnimation<Color>(AppTheme.brand600),
            ),
          ),
        ],
      ),
    ).animate().fadeIn(duration: 300.ms);
  }

  Future<void> _pickFile() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'],
    );

    if (result != null && result.files.single.path != null) {
      setState(() {
        _selectedFile = File(result.files.single.path!);
        _selectedFileName = result.files.single.name;
        if (_nameController.text.isEmpty) {
          _nameController.text = result.files.single.name
              .replaceAll(RegExp(r'\.[^.]+$'), '')
              .replaceAll('_', ' ');
        }
      });
    }
  }

  /// Map UI category string to backend docType
  String _categoryToDocType(String? category) {
    switch (category?.toLowerCase()) {
      case 'identity':
        return 'aadhaar';
      case 'education':
        return 'marksheet';
      case 'finance':
        return 'insurance';
      case 'medical':
        return 'medical';
      case 'legal':
        return 'certificate';
      default:
        return 'other';
    }
  }

  Future<void> _handleUpload() async {
    if (_selectedFile == null) return;

    setState(() => _isUploading = true);

    final docProvider = context.read<DocumentProvider>();
    final success = await docProvider.uploadDocument(
      file: _selectedFile!,
      name: _nameController.text.trim().isNotEmpty
          ? _nameController.text.trim()
          : _selectedFileName ?? 'Untitled',
      docType: _categoryToDocType(_selectedCategory),
      hasExpiry: _expiryDate != null,
      expiryDate: _expiryDate,
    );

    if (!mounted) return;
    setState(() => _isUploading = false);

    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('Document uploaded successfully!'),
          backgroundColor: const Color(0xFF20C997),
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(10),
          ),
        ),
      );
      Navigator.pop(context);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(docProvider.error ?? 'Upload failed'),
          backgroundColor: const Color(0xFFFA5252),
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(10),
          ),
        ),
      );
    }
  }
}
