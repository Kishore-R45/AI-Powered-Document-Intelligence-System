import { FileText, Trash2, ExternalLink, Calendar, Tag } from 'lucide-react';
import Card from '../common/Card';
import Badge from '../common/Badge';
import Button from '../common/Button';
import { formatDate, isExpired, isExpiringSoon } from '../../utils/formatters';
import { DOCUMENT_TYPES } from '../../utils/constants';

/**
 * Individual document card with metadata and actions.
 *
 * @param {object} document - Document metadata object
 * @param {function} onDelete - Called with document ID
 * @param {function} onView - Called with document ID
 */
export default function DocumentCard({ document, onDelete, onView }) {
  const typeLabel = DOCUMENT_TYPES.find((t) => t.value === document.type)?.label || 'Document';

  const getExpiryBadge = () => {
    if (!document.expiryDate) return null;
    if (isExpired(document.expiryDate)) {
      return <Badge variant="error" size="sm" dot>Expired</Badge>;
    }
    if (isExpiringSoon(document.expiryDate)) {
      return <Badge variant="warning" size="sm" dot>Expiring Soon</Badge>;
    }
    return <Badge variant="success" size="sm" dot>Active</Badge>;
  };

  return (
    <Card hover className="group">
      <div className="flex items-start gap-4">
        {/* File icon */}
        <div className="w-10 h-10 bg-brand-50 rounded-lg flex items-center justify-center shrink-0">
          <FileText size={20} className="text-brand-600" />
        </div>

        {/* Document info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <h4 className="text-sm font-semibold text-neutral-900 truncate">
              {document.name}
            </h4>
            {getExpiryBadge()}
          </div>

          <div className="flex items-center gap-4 mt-2 text-xs text-neutral-500">
            <span className="flex items-center gap-1">
              <Tag size={12} />
              {typeLabel}
            </span>
            <span className="flex items-center gap-1">
              <Calendar size={12} />
              {formatDate(document.uploadDate)}
            </span>
          </div>

          {document.expiryDate && (
            <p className="text-xs text-neutral-400 mt-1">
              Expires: {formatDate(document.expiryDate)}
            </p>
          )}
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2 mt-4 pt-4 border-t border-neutral-100">
        <Button
          variant="outline"
          size="sm"
          leftIcon={<ExternalLink size={14} />}
          onClick={() => onView(document.id)}
        >
          View
        </Button>
        <Button
          variant="ghost"
          size="sm"
          leftIcon={<Trash2 size={14} />}
          onClick={() => onDelete(document.id)}
          className="text-error-500 hover:bg-error-50 hover:text-error-700"
        >
          Delete
        </Button>
      </div>
    </Card>
  );
}