import { useState } from 'react';
import DocumentCard from './DocumentCard';
import EmptyState from '../common/EmptyState';
import ConfirmDialog from '../common/ConfirmDialog';
import { FileText, Search } from 'lucide-react';
import Input from '../common/Input';

/**
 * Filterable list of uploaded documents.
 *
 * @param {Array} documents - Array of document metadata
 * @param {function} onDelete - Called with document ID to delete
 * @param {function} onView - Called with document ID to view
 * @param {boolean} deleteLoading - Shows loading state on delete confirm
 */
export default function DocumentList({ documents = [], onDelete, onView, deleteLoading = false }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [deleteTarget, setDeleteTarget] = useState(null);

  const filtered = documents.filter((doc) => {
    const matchesSearch = doc.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = filterType === 'all' || doc.type === filterType;
    return matchesSearch && matchesType;
  });

  const handleDeleteConfirm = () => {
    if (deleteTarget) {
      onDelete(deleteTarget);
      setDeleteTarget(null);
    }
  };

  return (
    <div>
      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <div className="flex-1">
          <Input
            placeholder="Search documents..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            leftIcon={<Search size={18} />}
          />
        </div>
        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          className="block rounded-lg border border-neutral-300 bg-white px-3.5 py-2.5 text-sm text-neutral-700 focus:ring-2 focus:ring-brand-500 focus:border-brand-500 outline-none"
          aria-label="Filter by document type"
        >
          <option value="all">All types</option>
          <option value="insurance">Insurance</option>
          <option value="academic">Academic</option>
          <option value="id">Identification</option>
          <option value="financial">Financial</option>
          <option value="medical">Medical</option>
          <option value="general">General</option>
        </select>
      </div>

      {/* Document grid */}
      {filtered.length === 0 ? (
        <EmptyState
          icon={FileText}
          title={documents.length === 0 ? 'No documents uploaded' : 'No documents match your filters'}
          description={documents.length === 0
            ? 'Upload your first document to get started.'
            : 'Try adjusting your search or filter criteria.'
          }
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {filtered.map((doc) => (
            <DocumentCard
              key={doc.id}
              document={doc}
              onDelete={() => setDeleteTarget(doc.id)}
              onView={onView}
            />
          ))}
        </div>
      )}

      {/* Delete confirmation */}
      <ConfirmDialog
        isOpen={deleteTarget !== null}
        onClose={() => setDeleteTarget(null)}
        onConfirm={handleDeleteConfirm}
        title="Delete Document"
        message="Are you sure you want to delete this document? This action cannot be undone and the document will be permanently removed from your vault."
        confirmLabel="Delete"
        loading={deleteLoading}
      />
    </div>
  );
}