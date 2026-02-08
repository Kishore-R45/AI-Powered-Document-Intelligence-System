import { useState, useRef, useCallback } from 'react';
import { Upload, FileText, X, CheckCircle } from 'lucide-react';
import { clsx } from 'clsx';
import { ACCEPTED_FILE_TYPES, MAX_FILE_SIZE } from '../../utils/constants';
import { formatFileSize } from '../../utils/formatters';

/**
 * Drag-and-drop file upload zone with preview.
 * Accepts PDF and image files up to MAX_FILE_SIZE.
 *
 * @param {function} onFileSelect - Called with the selected File object
 * @param {File|null} selectedFile - Currently selected file (controlled)
 * @param {function} onClear - Clears the selected file
 */
export default function UploadZone({ onFileSelect, selectedFile, onClear }) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [error, setError] = useState('');
  const inputRef = useRef(null);

  const validateFile = (file) => {
    const acceptedTypes = Object.keys(ACCEPTED_FILE_TYPES);
    if (!acceptedTypes.includes(file.type)) {
      return 'File type not supported. Please upload a PDF or image file.';
    }
    if (file.size > MAX_FILE_SIZE) {
      return `File size exceeds ${formatFileSize(MAX_FILE_SIZE)} limit.`;
    }
    return '';
  };

  const handleFile = useCallback((file) => {
    const validationError = validateFile(file);
    if (validationError) {
      setError(validationError);
      return;
    }
    setError('');
    onFileSelect(file);
  }, [onFileSelect]);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  }, [handleFile]);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleInputChange = (e) => {
    const file = e.target.files[0];
    if (file) handleFile(file);
    // Reset input value to allow re-selecting the same file
    e.target.value = '';
  };

  if (selectedFile) {
    return (
      <div className="border-2 border-success-500 border-dashed rounded-xl p-6 bg-success-50">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-success-50 border border-success-200 rounded-lg flex items-center justify-center">
            <FileText size={24} className="text-success-500" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-neutral-900 truncate">{selectedFile.name}</p>
            <p className="text-xs text-neutral-500 mt-0.5">{formatFileSize(selectedFile.size)}</p>
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle size={20} className="text-success-500" />
            <button
              type="button"
              onClick={onClear}
              className="p-1.5 rounded-lg text-neutral-400 hover:text-neutral-600 hover:bg-neutral-100 transition-colors"
              aria-label="Remove file"
            >
              <X size={18} />
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => inputRef.current?.click()}
        className={clsx(
          'border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200',
          isDragOver
            ? 'border-brand-400 bg-brand-50'
            : 'border-neutral-300 hover:border-brand-300 hover:bg-neutral-25',
          error && 'border-error-500 bg-error-50'
        )}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            inputRef.current?.click();
          }
        }}
        aria-label="Upload document"
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.jpg,.jpeg,.png,.webp"
          onChange={handleInputChange}
          className="hidden"
          aria-hidden="true"
        />
        <div className="w-12 h-12 bg-neutral-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <Upload size={24} className={isDragOver ? 'text-brand-500' : 'text-neutral-400'} />
        </div>
        <p className="text-sm font-medium text-neutral-700 mb-1">
          {isDragOver ? 'Drop your file here' : 'Click to upload or drag and drop'}
        </p>
        <p className="text-xs text-neutral-500">
          PDF, JPG, PNG, or WEBP (max {formatFileSize(MAX_FILE_SIZE)})
        </p>
      </div>
      {error && (
        <p className="mt-2 text-sm text-error-500" role="alert">{error}</p>
      )}
    </div>
  );
}