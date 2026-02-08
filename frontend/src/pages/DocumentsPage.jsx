import { useEffect, useContext, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload } from 'lucide-react';
import DocumentList from '../components/documents/DocumentList';
import Button from '../components/common/Button';
import Spinner from '../components/common/Spinner';
import useDocuments from '../hooks/useDocuments';
import { ToastContext } from '../context/ToastContext';
import { ROUTES } from '../utils/constants';

/**
 * Documents listing page.
 * Shows all uploaded documents with search, filter, view, and delete.
 */
export default function DocumentsPage() {
  const navigate = useNavigate();
  const { toast } = useContext(ToastContext);
  const {
    documents,
    loading,
    fetchDocuments,
    deleteDocument,
  } = useDocuments();

  const [deleteLoading, setDeleteLoading] = useState(false);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  const handleDelete = async (documentId) => {
    setDeleteLoading(true);
    const result = await deleteDocument(documentId);

    if (result.success) {
      toast.success('Document deleted successfully.');
    } else {
      toast.error(result.error || 'Failed to delete document.');
    }
    setDeleteLoading(false);
  };

  const handleView = (documentId) => {
    const baseUrl = import.meta.env.VITE_API_BASE_URL;
    window.open(`${baseUrl}/documents/${documentId}/view`, '_blank', 'noopener,noreferrer');
  };

  if (loading && documents.length === 0) {
    return (
      <div className="flex items-center justify-center py-32">
        <Spinner size="xl" className="text-brand-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="page-heading">My Documents</h1>
          <p className="page-subheading">
            {documents.length} document{documents.length !== 1 ? 's' : ''} in your vault
          </p>
        </div>
        <Button
          variant="primary"
          size="sm"
          leftIcon={<Upload size={16} />}
          onClick={() => navigate(ROUTES.UPLOAD)}
        >
          Upload Document
        </Button>
      </div>

      <DocumentList
        documents={documents}
        onDelete={handleDelete}
        onView={handleView}
        deleteLoading={deleteLoading}
      />
    </div>
  );
}