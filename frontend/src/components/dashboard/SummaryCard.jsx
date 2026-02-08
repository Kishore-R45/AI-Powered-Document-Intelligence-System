import Card from '../common/Card';
import { clsx } from 'clsx';

/**
 * Dashboard summary card showing a metric with an icon.
 *
 * @param {string} title - Metric label
 * @param {string|number} value - Metric value
 * @param {React.ComponentType} icon - Lucide icon component
 * @param {'default'|'brand'|'success'|'warning'|'error'} color
 */
export default function SummaryCard({ title, value, icon: Icon, color = 'default', subtitle }) {
  const iconColors = {
    default: 'bg-neutral-100 text-neutral-600',
    brand: 'bg-brand-50 text-brand-600',
    success: 'bg-success-50 text-success-500',
    warning: 'bg-warning-50 text-warning-500',
    error: 'bg-error-50 text-error-500',
  };

  return (
    <Card hover>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-neutral-500">{title}</p>
          <p className="text-2xl font-bold text-neutral-900 mt-1">{value}</p>
          {subtitle && (
            <p className="text-xs text-neutral-400 mt-1">{subtitle}</p>
          )}
        </div>
        {Icon && (
          <div className={clsx('w-10 h-10 rounded-lg flex items-center justify-center', iconColors[color])}>
            <Icon size={20} />
          </div>
        )}
      </div>
    </Card>
  );
}