import { useState } from 'react';
import { Shield } from 'lucide-react';
import SignupForm from '../components/auth/SignupForm';
import OTPVerification from '../components/auth/OTPVerification';
import useAuth from '../hooks/useAuth';
import { APP_NAME } from '../utils/constants';

/**
 * Signup page with dimmed background.
 * Two-step flow: registration → OTP verification.
 */
export default function SignupPage() {
  const { signup, verifyOTP, resendOTP } = useAuth();

  const [step, setStep] = useState('register');
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [serverError, setServerError] = useState('');
  const [otpError, setOtpError] = useState('');

  const handleSignup = async (formData) => {
    setLoading(true);
    setServerError('');

    const result = await signup(formData);

    if (result.success && result.requiresOTP) {
      setEmail(formData.email || result.email);
      setStep('verify');
    } else if (!result.success) {
      setServerError(result.error);
    }

    setLoading(false);
  };

  const handleVerifyOTP = async (otp) => {
    setLoading(true);
    setOtpError('');

    const result = await verifyOTP(email, otp);

    if (!result.success) {
      setOtpError(result.error);
    }

    setLoading(false);
  };

  const handleResendOTP = async () => {
    setOtpError('');
    const result = await resendOTP(email);
    if (!result.success) {
      setOtpError(result.error);
    }
  };

  return (
    <div className="auth-container bg-[#F6F7F9]">
      <div className="auth-card">
        <div className="text-center mb-8">
          <div className="w-12 h-12 bg-brand-600 rounded-xl flex items-center justify-center mx-auto mb-4">
            <Shield size={24} className="text-white" />
          </div>

          {step === 'register' ? (
            <>
              <h1 className="text-xl font-bold text-neutral-900">
                Create your account
              </h1>
              <p className="text-sm text-neutral-500 mt-1">
                Start securing your documents with {APP_NAME}
              </p>
            </>
          ) : (
            <>
              <h1 className="text-xl font-bold text-neutral-900">
                Verify your email
              </h1>
              <p className="text-sm text-neutral-500 mt-1">
                We sent a code to{' '}
                <span className="font-medium text-neutral-700">{email}</span>
              </p>
            </>
          )}
        </div>

        {step === 'register' ? (
          <SignupForm
            onSubmit={handleSignup}
            loading={loading}
            serverError={serverError}
          />
        ) : (
          <OTPVerification
            onVerify={handleVerifyOTP}
            onResend={handleResendOTP}
            loading={loading}
            error={otpError}
          />
        )}

        {step === 'verify' && (
          <div className="mt-6 text-center">
            <button
              onClick={() => {
                setStep('register');
                setOtpError('');
              }}
              className="text-sm text-neutral-500 hover:text-neutral-700 transition-colors"
            >
              ← Back to registration
            </button>
          </div>
        )}
      </div>
    </div>
  );
}