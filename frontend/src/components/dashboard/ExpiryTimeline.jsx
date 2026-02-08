import Card from '../common/Card';
import Badge from '../common/Badge';
import { formatDate, isExpired, isExpiringSoon } from '../../utils/formatters';
import { Clock, AlertTriangle } from 'lucide-react';

/**
 * Timeline of upcoming document expirations.
 *
 * @param {Array} documents - Documents with expiry dates, sorted by date
 */
export default function ExpiryTimeline({ documents = [] }) {
  const getExpiryStatus = (date) => {
    if (isExpired(date)) return { variant: 'error', label: 'Expired', icon: AlertTriangle };
    if (isExpiringSoon(date)) return { variant: 'warning', label: 'Expiring Soon', icon: Clock };
    return { variant: 'success', label: 'Active', icon: Clock };
  };

  return (
    <Card>
      <h3 className="text-base font-semibold text-neutral-900 mb-4">Expiry Timeline</h3>
      {documents.length === 0 ? (
        <p className="text-sm text-neutral-500 text-center py-8">No documents with expiry dates</p>
      ) : (
        <div className="space-y-3">
          {documents.map((doc, index) => {
            const status = getExpiryStatus(doc.expiryDate);
            const StatusIcon = status.icon;
            return (
              <div
                key={doc.id || index}
                className="flex items-center gap-3 p-3 rounded-lg border border-neutral-100 hover:bg-neutral-25 transition-colors"
              >
                <StatusIcon size={18} className={
                  status.variant === 'error' ? 'text-error-500' :
                  status.variant === 'warning' ? 'text-warning-500' :
                  'text-success-500'
                } />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-neutral-900 truncate">{doc.name}</p>
                  <p className="text-xs text-neutral-500">{formatDate(doc.expiryDate)}</p>
                </div>
                <Badge variant={status.variant} size="sm" dot>
                  {status.label}
                </Badge>
              </div>
            );
          })}
        </div>
      )}
    </Card>
  );
}