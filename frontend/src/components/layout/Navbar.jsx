import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Menu, X, Shield } from 'lucide-react';
import { APP_NAME, ROUTES } from '../../utils/constants';
import Button from '../common/Button';
import NotificationBell from '../notifications/NotificationBell';

/**
 * Top navigation bar.
 * - Public (unauthenticated): Shows only logo, Login, and Sign Up.
 *   No feature/section anchor links.
 * - Authenticated: Shows logo, notification bell, user avatar, and logout.
 *   No duplicate nav links (those live in the Sidebar).
 */
export default function Navbar({ isAuthenticated = false, user = null, onLogout }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const navigate = useNavigate();

  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-sm border-b border-neutral-200">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* ── Logo ── */}
          <Link
            to={isAuthenticated ? ROUTES.DASHBOARD : ROUTES.HOME}
            className="flex items-center gap-2.5"
          >
            <div className="w-8 h-8 bg-brand-600 rounded-lg flex items-center justify-center">
              <Shield size={18} className="text-white" />
            </div>
            <span className="text-lg font-bold text-neutral-900">{APP_NAME}</span>
          </Link>

          {/* ── Desktop right section ── */}
          <div className="hidden md:flex items-center gap-3">
            {isAuthenticated ? (
              <>
                <NotificationBell />
                <Link
                  to={ROUTES.PROFILE}
                  className="flex items-center gap-2 px-3 py-1.5 rounded-lg hover:bg-neutral-50 transition-colors"
                >
                  <div className="w-8 h-8 bg-brand-100 text-brand-700 rounded-full flex items-center justify-center text-sm font-semibold">
                    {user?.name?.charAt(0)?.toUpperCase() || 'U'}
                  </div>
                  <span className="text-sm font-medium text-neutral-700">
                    {user?.name?.split(' ')[0] || 'User'}
                  </span>
                </Link>
                <Button variant="ghost" size="sm" onClick={onLogout}>
                  Logout
                </Button>
              </>
            ) : (
              <>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => navigate(ROUTES.LOGIN)}
                >
                  Log in
                </Button>
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => navigate(ROUTES.SIGNUP)}
                >
                  Sign up
                </Button>
              </>
            )}
          </div>

          {/* ── Mobile menu button ── */}
          <button
            className="md:hidden p-2 rounded-lg text-neutral-600 hover:bg-neutral-100"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>

        {/* ── Mobile menu ── */}
        {mobileMenuOpen && (
          <div className="md:hidden py-4 border-t border-neutral-100 animate-slide-down">
            <div className="flex flex-col gap-1">
              {isAuthenticated ? (
                <>
                  {/* Mobile: show nav links since sidebar is hidden on mobile */}
                  <Link
                    to={ROUTES.DASHBOARD}
                    className="px-3 py-2.5 text-sm font-medium text-neutral-600 hover:bg-neutral-50 rounded-lg"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Dashboard
                  </Link>
                  <Link
                    to={ROUTES.UPLOAD}
                    className="px-3 py-2.5 text-sm font-medium text-neutral-600 hover:bg-neutral-50 rounded-lg"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Upload
                  </Link>
                  <Link
                    to={ROUTES.DOCUMENTS}
                    className="px-3 py-2.5 text-sm font-medium text-neutral-600 hover:bg-neutral-50 rounded-lg"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Documents
                  </Link>
                  <Link
                    to={ROUTES.CHAT}
                    className="px-3 py-2.5 text-sm font-medium text-neutral-600 hover:bg-neutral-50 rounded-lg"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Query
                  </Link>
                  <Link
                    to={ROUTES.NOTIFICATIONS}
                    className="px-3 py-2.5 text-sm font-medium text-neutral-600 hover:bg-neutral-50 rounded-lg"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Notifications
                  </Link>
                  <Link
                    to={ROUTES.PROFILE}
                    className="px-3 py-2.5 text-sm font-medium text-neutral-600 hover:bg-neutral-50 rounded-lg"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Profile
                  </Link>
                  <div className="pt-2 mt-2 border-t border-neutral-100">
                    <button
                      onClick={onLogout}
                      className="w-full text-left px-3 py-2.5 text-sm font-medium text-error-500 hover:bg-error-50 rounded-lg"
                    >
                      Logout
                    </button>
                  </div>
                </>
              ) : (
                <>
                  <div className="flex gap-2 px-3 pt-1">
                    <Button
                      variant="outline"
                      size="sm"
                      fullWidth
                      onClick={() => {
                        navigate(ROUTES.LOGIN);
                        setMobileMenuOpen(false);
                      }}
                    >
                      Log in
                    </Button>
                    <Button
                      variant="primary"
                      size="sm"
                      fullWidth
                      onClick={() => {
                        navigate(ROUTES.SIGNUP);
                        setMobileMenuOpen(false);
                      }}
                    >
                      Sign up
                    </Button>
                  </div>
                </>
              )}
            </div>
          </div>
        )}
      </nav>
    </header>
  );
}