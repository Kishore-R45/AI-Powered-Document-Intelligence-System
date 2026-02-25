import { Shield } from 'lucide-react';
import ForgotPasswordForm from '../components/auth/ForgotPasswordForm';

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
        </div>

        <ForgotPasswordForm />
      </div>
    </div>
  );
}
