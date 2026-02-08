import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FileText,
  Upload,
  Clock,
  MessageSquare,
  ArrowRight,
} from 'lucide-react';
import SummaryCard from '../components/dashboard/SummaryCard';
import RecentActivity from '../components/dashboard/RecentActivity';
import ExpiryTimeline from '../components/dashboard/ExpiryTimeline';
import Button from '../components/common/Button';
import Spinner from '../components/common/Spinner';
import useAuth from '../hooks/useAuth';
import useDocuments from '../hooks/useDocuments';
import { ROUTES } from '../utils/constants';
import { isExpiringSoon, isExpired } from '../utils/formatters';

/**
 * Dashboard page.
 * Shows high-level overview: summary metrics, recent activity, and expiry timeline.
 */
export default function DashboardPage() {
  const { user } = useAuth();
  const { documents, loading, fetchDocuments } = useDocuments();
  const navigate = useNavigate();

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  /**
   * Derive summary metrics from document list.
   */
  const totalDocuments = documents.length;

  const expiringDocuments = documents.filter(
    (doc) => doc.expiryDate && (isExpiringSoon(doc.expiryDate) || isExpired(doc.expiryDate))
  );

  const documentsWithExpiry = documents
    .filter((doc) => doc.expiryDate)
    .sort((a, b) => new Date(a.expiryDate) - new Date(b.expiryDate));

  const recentUploads = documents
    .slice()
    .sort((a, b) => new Date(b.uploadDate) - new Date(a.uploadDate))
    .slice(0, 5);

  /**
   * Build recent activity from recent uploads.
   * In production, this would come from a dedicated activity API endpoint.
   */
  const recentActivity = recentUploads.map((doc) => ({
    id: doc.id,
    type: 'upload',
    documentName: doc.name,
    timestamp: doc.uploadDate,
  }));

  if (loading && documents.length === 0) {
    return (
      <div className="flex items-center justify-center py-32">
        <Spinner size="xl" className="text-brand-600" />
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Page header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="page-heading">
            Welcome back, {user?.name?.split(' ')[0] || 'User'}
          </h1>
          <p className="page-subheading">
            Here's an overview of your document vault.
          </p>
        </div>
        <div className="flex gap-3">
          <Button
            variant="outline"
            size="sm"
            leftIcon={<MessageSquare size={16} />}
            onClick={() => navigate(ROUTES.CHAT)}
          >
            Query Documents
          </Button>
          <Button
            variant="primary"
            size="sm"
            leftIcon={<Upload size={16} />}
            onClick={() => navigate(ROUTES.UPLOAD)}
          >
            Upload
          </Button>
        </div>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <SummaryCard
          title="Total Documents"
          value={totalDocuments}
          icon={FileText}
          color="brand"
          subtitle="In your vault"
        />
        <SummaryCard
          title="With Expiry Dates"
          value={documentsWithExpiry.length}
          icon={Clock}
          color="default"
          subtitle="Being tracked"
        />
        <SummaryCard
          title="Expiring Soon"
          value={expiringDocuments.length}
          icon={Clock}
          color={expiringDocuments.length > 0 ? 'warning' : 'success'}
          subtitle={expiringDocuments.length > 0 ? 'Need attention' : 'All good'}
        />
        <SummaryCard
          title="Recently Uploaded"
          value={recentUploads.length}
          icon={Upload}
          color="success"
          subtitle="Last 5 documents"
        />
      </div>

      {/* Two-column layout: Activity + Expiry */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RecentActivity activities={recentActivity} />
        <ExpiryTimeline documents={documentsWithExpiry.slice(0, 6)} />
      </div>

      {/* Quick action if no documents */}
      {totalDocuments === 0 && (
        <div className="text-center py-12 bg-white rounded-xl border border-neutral-200">
          <div className="w-16 h-16 bg-brand-50 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <Upload size={28} className="text-brand-600" />
          </div>
          <h3 className="text-lg font-semibold text-neutral-900 mb-2">
            Your vault is empty
          </h3>
          <p className="text-sm text-neutral-500 mb-6 max-w-sm mx-auto">
            Upload your first document to start organizing and querying your personal information.
          </p>
          <Button
            variant="primary"
            rightIcon={<ArrowRight size={16} />}
            onClick={() => navigate(ROUTES.UPLOAD)}
          >
            Upload Your First Document
          </Button>
        </div>
      )}
    </div>
  );
}