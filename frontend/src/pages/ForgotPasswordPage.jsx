import { Shield } from 'lucide-react';
import ForgotPasswordForm from '../components/auth/ForgotPasswordForm';
import { APP_NAME } from '../utils/constants';

/**
 * Forgot Password page.
 */
export default function ForgotPasswordPage() {
  return (
    <div className="auth-container bg-[#F6F7F9]">
      <div className="auth-card">
        <div className="text-center mb-8">
          <div className="w-12 h-12 bg-brand-600 rounded-xl flex items-center justify-center mx-auto mb-4">
            <Shield size={24} className="text-white" />
          </div>
          <h1 className="text-xl font-bold text-neutral-900">
            Reset Password
          </h1>
          <p className="text-sm text-neutral-500 mt-1">
            Recover your {APP_NAME} account
          </p>
        </div>

        <ForgotPasswordForm />
      </div>
    </div>
  );
}
