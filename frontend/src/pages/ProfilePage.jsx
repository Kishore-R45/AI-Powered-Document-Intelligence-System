import { useState, useContext } from 'react';
import { LogOut, Shield } from 'lucide-react';
import ProfileDetails from '../components/profile/ProfileDetails';
import ChangePasswordForm from '../components/profile/ChangePasswordForm';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import ConfirmDialog from '../components/common/ConfirmDialog';
import useAuth from '../hooks/useAuth';
import { ToastContext } from '../context/ToastContext';
import api from '../api/axios';
import ENDPOINTS from '../api/endpoints';

/**
 * Profile and account settings page.
 * Includes profile details, password change, and session management.
 */
export default function ProfilePage() {
  const { user, logoutAllSessions } = useAuth();
  const { toast } = useContext(ToastContext);

  // Change password state
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [passwordError, setPasswordError] = useState('');
  const [passwordSuccess, setPasswordSuccess] = useState('');

  // Logout all sessions state
  const [showLogoutAll, setShowLogoutAll] = useState(false);
  const [logoutAllLoading, setLogoutAllLoading] = useState(false);

  /**
   * Handle password change submission.
   */
  const handleChangePassword = async ({ currentPassword, newPassword }) => {
    setPasswordLoading(true);
    setPasswordError('');
    setPasswordSuccess('');

    try {
      await api.post(ENDPOINTS.USER.CHANGE_PASSWORD, {
        currentPassword,
        newPassword,
      });
      setPasswordSuccess('Password updated successfully.');
      toast.success('Password updated successfully.');
    } catch (error) {
      const message =
        error.response?.data?.message || 'Failed to update password. Please try again.';
      setPasswordError(message);
    } finally {
      setPasswordLoading(false);
    }
  };

  /**
   * Handle logout from all sessions.
   */
  const handleLogoutAllSessions = async () => {
    setLogoutAllLoading(true);
    const result = await logoutAllSessions();

    if (!result.success) {
      toast.error(result.error);
    }
    setLogoutAllLoading(false);
    setShowLogoutAll(false);
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6 animate-fade-in">
      {/* Page header */}
      <div>
        <h1 className="page-heading">Account Settings</h1>
        <p className="page-subheading">
          Manage your profile, security, and account preferences.
        </p>
      </div>

      {/* Profile details */}
      <ProfileDetails user={user} />

      {/* Change password */}
      <ChangePasswordForm
        onSubmit={handleChangePassword}
        loading={passwordLoading}
        error={passwordError}
        success={passwordSuccess}
      />

      {/* Security section */}
      <Card>
        <h3 className="text-base font-semibold text-neutral-900 mb-4 flex items-center gap-2">
          <Shield size={18} className="text-neutral-500" />
          Security
        </h3>

        <div className="space-y-4">
          {/* Logout all sessions */}
          <div className="flex items-center justify-between p-4 bg-neutral-50 rounded-lg border border-neutral-200">
            <div>
              <p className="text-sm font-medium text-neutral-900">
                Logout from all devices
              </p>
              <p className="text-xs text-neutral-500 mt-0.5">
                This will sign you out from all active sessions on every device.
              </p>
            </div>
            <Button
              variant="outline"
              size="sm"
              leftIcon={<LogOut size={14} />}
              onClick={() => setShowLogoutAll(true)}
            >
              Logout All
            </Button>
          </div>

          {/* Security notice */}
          <div className="p-4 bg-brand-50 rounded-lg border border-brand-200">
            <p className="text-xs text-brand-700 leading-relaxed">
              <span className="font-semibold">Security Reminder:</span> Never share your
              password or OTP codes with anyone. Our team will never ask for your password.
              Enable strong passwords and change them periodically.
            </p>
          </div>
        </div>
      </Card>

      {/* Logout all confirmation dialog */}
      <ConfirmDialog
        isOpen={showLogoutAll}
        onClose={() => setShowLogoutAll(false)}
        onConfirm={handleLogoutAllSessions}
        title="Logout from All Devices"
        message="This will immediately sign you out from all active sessions, including this one. You will need to sign in again."
        confirmLabel="Logout All"
        variant="danger"
        loading={logoutAllLoading}
      />
    </div>
  );
}