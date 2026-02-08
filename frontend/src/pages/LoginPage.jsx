import { useState } from 'react';
import { Shield } from 'lucide-react';
import LoginForm from '../components/auth/LoginForm';
import useAuth from '../hooks/useAuth';
import { APP_NAME } from '../utils/constants';

/**
 * Login page with dimmed background.
 */
export default function LoginPage() {
  const { login } = useAuth();
  const [loading, setLoading] = useState(false);
  const [serverError, setServerError] = useState('');

  const handleLogin = async (formData) => {
    setLoading(true);
    setServerError('');

    const result = await login(formData.email, formData.password);

    if (!result.success) {
      setServerError(result.error);
    }

    setLoading(false);
  };

  return (
    <div className="auth-container bg-[#F6F7F9]">
      <div className="auth-card">
        <div className="text-center mb-8">
          <div className="w-12 h-12 bg-brand-600 rounded-xl flex items-center justify-center mx-auto mb-4">
            <Shield size={24} className="text-white" />
          </div>
          <h1 className="text-xl font-bold text-neutral-900">
            Welcome back
          </h1>
          <p className="text-sm text-neutral-500 mt-1">
            Sign in to your {APP_NAME} account
          </p>
        </div>

        <LoginForm
          onSubmit={handleLogin}
          loading={loading}
          serverError={serverError}
        />
      </div>
    </div>
  );
}