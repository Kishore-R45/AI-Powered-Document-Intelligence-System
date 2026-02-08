import Card from '../common/Card';
import Badge from '../common/Badge';
import { formatRelativeTime } from '../../utils/formatters';
import { Upload, MessageSquare, Trash2, FileText } from 'lucide-react';

/**
 * Recent activity feed for the dashboard.
 *
 * @param {Array} activities - Array of activity objects
 */

const activityIcons = {
  upload: Upload,
  query: MessageSquare,
  delete: Trash2,
  view: FileText,
};

const activityLabels = {
  upload: 'Uploaded',
  query: 'Queried',
  delete: 'Deleted',
  view: 'Viewed',
};

export default function RecentActivity({ activities = [] }) {
  return (
    <Card>
      <h3 className="text-base font-semibold text-neutral-900 mb-4">Recent Activity</h3>
      {activities.length === 0 ? (
        <p className="text-sm text-neutral-500 text-center py-8">No recent activity</p>
      ) : (
        <div className="space-y-4">
          {activities.map((activity, index) => {
            const Icon = activityIcons[activity.type] || FileText;
            return (
              <div key={activity.id || index} className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-neutral-100 flex items-center justify-center shrink-0 mt-0.5">
                  <Icon size={16} className="text-neutral-500" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-neutral-900">
                    <span className="font-medium">{activityLabels[activity.type] || 'Action'}</span>{' '}
                    {activity.documentName}
                  </p>
                  <p className="text-xs text-neutral-400 mt-0.5">
                    {formatRelativeTime(activity.timestamp)}
                  </p>
                </div>
                {activity.badge && (
                  <Badge variant={activity.badgeVariant || 'default'} size="sm">
                    {activity.badge}
                  </Badge>
                )}
              </div>
            );
          })}
        </div>
      )}
    </Card>
  );
}