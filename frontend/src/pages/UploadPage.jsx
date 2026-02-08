import { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, CheckCircle } from 'lucide-react';
import UploadZone from '../components/documents/UploadZone';
import DocumentTypeSelect from '../components/documents/DocumentTypeSelect';
import ExpiryToggle from '../components/documents/ExpiryToggle';
import Input from '../components/common/Input';
import Button from '../components/common/Button';
import Card from '../components/common/Card';
import useDocuments from '../hooks/useDocuments';
import { ToastContext } from '../context/ToastContext';
import { ROUTES } from '../utils/constants';

/**
 * Document upload page.
 * Multi-step form: file selection → metadata → confirmation.
 */
export default function UploadPage() {
  const navigate = useNavigate();
  const { toast } = useContext(ToastContext);
  const { uploadDocument, uploading, uploadProgress } = useDocuments();

  // Form state
  const [file, setFile] = useState(null);
  const [documentName, setDocumentName] = useState('');
  const [documentType, setDocumentType] = useState('');
  const [hasExpiry, setHasExpiry] = useState(false);
  const [expiryDate, setExpiryDate] = useState('');
  const [errors, setErrors] = useState({});
  const [uploadSuccess, setUploadSuccess] = useState(false);

  /**
   * Validate form before submission.
   */
  const validate = () => {
    const newErrors = {};
    if (!file) newErrors.file = 'Please select a file to upload.';
    if (!documentType) newErrors.type = 'Please select a document type.';
    if (hasExpiry && !expiryDate) newErrors.expiry = 'Please select an expiry date.';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  /**
   * Handle form submission.
   */
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validate()) return;

    const metadata = {
      name: documentName.trim() || file.name.replace(/\.[^/.]+$/, ''),
      type: documentType,
      hasExpiry,
      expiryDate: hasExpiry ? expiryDate : null,
    };

    const result = await uploadDocument(file, metadata);

    if (result.success) {
      setUploadSuccess(true);
      toast.success('Document uploaded successfully!');
    } else {
      toast.error(result.error || 'Upload failed. Please try again.');
    }
  };

  /**
   * Reset form for another upload.
   */
  const handleUploadAnother = () => {
    setFile(null);
    setDocumentName('');
    setDocumentType('');
    setHasExpiry(false);
    setExpiryDate('');
    setErrors({});
    setUploadSuccess(false);
  };

  // ── Success State ──
  if (uploadSuccess) {
    return (
      <div className="max-w-lg mx-auto animate-fade-in">
        <Card className="text-center py-12">
          <div className="w-16 h-16 bg-success-50 rounded-full flex items-center justify-center mx-auto mb-6">
            <CheckCircle size={32} className="text-success-500" />
          </div>
          <h2 className="text-xl font-bold text-neutral-900 mb-2">
            Document Uploaded
          </h2>
          <p className="text-sm text-neutral-500 mb-8 max-w-sm mx-auto">
            Your document has been securely uploaded and is now being processed.
            You can query it shortly.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
            <Button variant="primary" onClick={handleUploadAnother}>
              Upload Another
            </Button>
            <Button variant="outline" onClick={() => navigate(ROUTES.DOCUMENTS)}>
              View Documents
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  // ── Upload Form ──
  return (
    <div className="max-w-2xl mx-auto space-y-6 animate-fade-in">
      {/* Page header */}
      <div>
        <h1 className="page-heading">Upload Document</h1>
        <p className="page-subheading">
          Add a new document to your secure vault. Supported formats: PDF, JPG, PNG, WEBP.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* File upload zone */}
        <Card>
          <h3 className="text-sm font-semibold text-neutral-900 mb-4">
            Select File
          </h3>
          <UploadZone
            onFileSelect={setFile}
            selectedFile={file}
            onClear={() => {
              setFile(null);
              setErrors((prev) => ({ ...prev, file: '' }));
            }}
          />
          {errors.file && (
            <p className="mt-2 text-sm text-error-500" role="alert">
              {errors.file}
            </p>
          )}
        </Card>

        {/* Document metadata */}
        <Card>
          <h3 className="text-sm font-semibold text-neutral-900 mb-4">
            Document Details
          </h3>
          <div className="space-y-6">
            {/* Optional custom name */}
            <Input
              label="Document name"
              placeholder={file ? file.name.replace(/\.[^/.]+$/, '') : 'Enter a name for this document'}
              value={documentName}
              onChange={(e) => setDocumentName(e.target.value)}
              helperText="Optional. Defaults to file name if not specified."
            />

            {/* Document type */}
            <div>
              <DocumentTypeSelect
                value={documentType}
                onChange={(type) => {
                  setDocumentType(type);
                  setErrors((prev) => ({ ...prev, type: '' }));
                }}
              />
              {errors.type && (
                <p className="mt-2 text-sm text-error-500" role="alert">
                  {errors.type}
                </p>
              )}
            </div>

            {/* Expiry toggle */}
            <ExpiryToggle
              hasExpiry={hasExpiry}
              onToggle={(val) => {
                setHasExpiry(val);
                if (!val) {
                  setExpiryDate('');
                  setErrors((prev) => ({ ...prev, expiry: '' }));
                }
              }}
              expiryDate={expiryDate}
              onDateChange={(date) => {
                setExpiryDate(date);
                setErrors((prev) => ({ ...prev, expiry: '' }));
              }}
            />
            {errors.expiry && (
              <p className="mt-2 text-sm text-error-500" role="alert">
                {errors.expiry}
              </p>
            )}
          </div>
        </Card>

        {/* Upload progress bar */}
        {uploading && (
          <Card padding="sm">
            <div className="flex items-center gap-3">
              <Upload size={18} className="text-brand-600 animate-pulse" />
              <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium text-neutral-700">Uploading...</span>
                  <span className="text-sm text-neutral-500">{uploadProgress}%</span>
                </div>
                <div className="w-full h-2 bg-neutral-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-brand-600 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
              </div>
            </div>
          </Card>
        )}

        {/* Submit */}
        <div className="flex items-center justify-end gap-3">
          <Button
            variant="outline"
            onClick={() => navigate(ROUTES.DOCUMENTS)}
            disabled={uploading}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            variant="primary"
            leftIcon={<Upload size={16} />}
            loading={uploading}
            disabled={!file}
          >
            Upload Document
          </Button>
        </div>
      </form>
    </div>
  );
}