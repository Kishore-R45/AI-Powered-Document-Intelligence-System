import { User, Mail, Calendar } from 'lucide-react';
import Card from '../common/Card';
import { formatDate } from '../../utils/formatters';

/**
 * Displays user profile information.
 *
 * @param {object} user - { name, email, createdAt }
 */
export default function ProfileDetails({ user }) {
  if (!user) return null;

  const details = [
    { icon: User, label: 'Full name', value: user.name },
    { icon: Mail, label: 'Email', value: user.email },
    { icon: Calendar, label: 'Member since', value: formatDate(user.createdAt) },
  ];

  return (
    <Card>
      <div className="flex items-center gap-4 mb-6">
        <div className="w-16 h-16 bg-brand-100 text-brand-700 rounded-full flex items-center justify-center text-2xl font-bold">
          {user.name?.charAt(0)?.toUpperCase() || 'U'}
        </div>
        <div>
          <h2 className="text-lg font-semibold text-neutral-900">{user.name}</h2>
          <p className="text-sm text-neutral-500">{user.email}</p>
        </div>
      </div>

      <div className="space-y-4">
        {details.map(({ icon: Icon, label, value }) => (
          <div key={label} className="flex items-center gap-3 py-3 border-t border-neutral-100">
            <Icon size={18} className="text-neutral-400 shrink-0" />
            <div>
              <p className="text-xs text-neutral-500">{label}</p>
              <p className="text-sm font-medium text-neutral-900">{value}</p>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}