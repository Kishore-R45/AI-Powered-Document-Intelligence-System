import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Upload,
  FileText,
  MessageSquare,
  User,
  Bell,
} from 'lucide-react';
import { clsx } from 'clsx';
import { ROUTES } from '../../utils/constants';

/**
 * Sidebar navigation for the authenticated app layout.
 * Uses NavLink for active state highlighting.
 */
const navItems = [
  { path: ROUTES.DASHBOARD, label: 'Dashboard', icon: LayoutDashboard },
  { path: ROUTES.UPLOAD, label: 'Upload', icon: Upload },
  { path: ROUTES.DOCUMENTS, label: 'Documents', icon: FileText },
  { path: ROUTES.CHAT, label: 'Query', icon: MessageSquare },
  { path: ROUTES.NOTIFICATIONS, label: 'Notifications', icon: Bell },
  { path: ROUTES.PROFILE, label: 'Profile', icon: User },
];

export default function Sidebar() {
  return (
    <aside className="hidden lg:flex lg:flex-col w-64 bg-white border-r border-neutral-200 sticky top-16 h-[calc(100vh-4rem)] self-start overflow-y-auto">
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map(({ path, label, icon: Icon }) => (
          <NavLink
            key={path}
            to={path}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors duration-150',
                isActive
                  ? 'bg-brand-50 text-brand-700'
                  : 'text-neutral-600 hover:bg-neutral-50 hover:text-neutral-900'
              )
            }
          >
            <Icon size={20} />
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}