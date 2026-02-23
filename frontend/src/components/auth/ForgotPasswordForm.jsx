import { useState, useRef } from 'react';
import { Link } from 'react-router-dom';
import { Mail, Lock, Eye, EyeOff, ArrowLeft, CheckCircle } from 'lucide-react';
import Input from '../common/Input';
import Button from '../common/Button';
import OTPVerification from './OTPVerification';
import { validateEmail, validatePassword } from '../../utils/validators';
import { ROUTES } from '../../utils/constants';
import api from '../../api/axios';
import ENDPOINTS from '../../api/endpoints';

/**
 * Forgot Password form with 3-step flow:
 * 1. Enter email
 * 2. Verify OTP
 * 3. Set new password
 */
export default function ForgotPasswordForm() {
  const [step, setStep] = useState(1); // 1=email, 2=otp, 3=new password, 4=success
  const [email, setEmail] = useState('');
  const [resetToken, setResetToken] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [errors, setErrors] = useState({});
  const [serverError, setServerError] = useState('');
  const [loading, setLoading] = useState(false);

  // Step 1: Send OTP to email
  const handleSendOTP = async (e) => {
    e.preventDefault();
    setServerError('');

    const emailError = validateEmail(email);
    if (emailError) {
      setErrors({ email: emailError });
      return;
    }
    setErrors({});

    setLoading(true);
    try {
      await api.post(ENDPOINTS.AUTH.FORGOT_PASSWORD, { email });
      setStep(2);
    } catch (error) {
      setServerError(
        error.response?.data?.message ||
        error.response?.data?.error ||
        'Failed to send verification code. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  // Step 2: Verify OTP
  const handleVerifyOTP = async (otpCode) => {
    setServerError('');
    setLoading(true);
    try {
      const response = await api.post(ENDPOINTS.AUTH.VERIFY_RESET_OTP, {
        email,
        otp: otpCode,
      });
      const data = response.data;
      setResetToken(data.resetToken || data.data?.resetToken);
      setStep(3);
    } catch (error) {
      setServerError(
        error.response?.data?.message ||
        error.response?.data?.error ||
        'Invalid verification code. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  // Step 2: Resend OTP
  const handleResendOTP = async () => {
    setServerError('');
    setLoading(true);
    try {
      await api.post(ENDPOINTS.AUTH.VERIFY_RESET_OTP, { email, resend: true });
    } catch (error) {
      setServerError(
        error.response?.data?.message || 'Failed to resend code. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  // Step 3: Reset password
  const handleResetPassword = async (e) => {
    e.preventDefault();
    setServerError('');

    const newErrors = {};
    const passwordError = validatePassword(newPassword);
    if (passwordError) newErrors.newPassword = passwordError;
    if (newPassword !== confirmPassword) newErrors.confirmPassword = 'Passwords do not match';
    if (!confirmPassword) newErrors.confirmPassword = 'Please confirm your password';

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }
    setErrors({});

    setLoading(true);
    try {
      await api.post(ENDPOINTS.AUTH.RESET_PASSWORD, {
        email,
        resetToken,
        newPassword,
      });
      setStep(4);
    } catch (error) {
      setServerError(
        error.response?.data?.message ||
        error.response?.data?.error ||
        'Failed to reset password. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  // Step 1: Email input
  if (step === 1) {
    return (
      <form onSubmit={handleSendOTP} className="space-y-5" noValidate>
        <div className="text-center mb-2">
          <h2 className="text-lg font-semibold text-neutral-900">Forgot Password</h2>
          <p className="text-sm text-neutral-500 mt-1">
            Enter your email address and we'll send you a verification code.
          </p>
        </div>

        {serverError && (
          <div className="p-3 rounded-lg bg-error-50 border border-red-200 text-sm text-error-700" role="alert">
            {serverError}
          </div>
        )}

        <Input
          label="Email address"
          name="email"
          type="email"
          placeholder="you@example.com"
          value={email}
          onChange={(e) => {
            setEmail(e.target.value);
            if (errors.email) setErrors({});
          }}
          error={errors.email}
          required
          leftIcon={<Mail size={18} />}
          autoComplete="email"
        />

        <Button type="submit" variant="primary" fullWidth loading={loading}>
          Send Verification Code
        </Button>

        <p className="text-center text-sm text-neutral-600">
          <Link
            to={ROUTES.LOGIN}
            className="inline-flex items-center gap-1 font-medium text-brand-600 hover:text-brand-700 transition-colors"
          >
            <ArrowLeft size={14} />
            Back to Login
          </Link>
        </p>
      </form>
    );
  }

  // Step 2: OTP verification
  if (step === 2) {
    return (
      <div className="space-y-5">
        {serverError && (
          <div className="p-3 rounded-lg bg-error-50 border border-red-200 text-sm text-error-700 text-center" role="alert">
            {serverError}
          </div>
        )}

        <OTPVerification
          onVerify={handleVerifyOTP}
          onResend={handleResendOTP}
          loading={loading}
          error=""
        />

        <p className="text-center text-sm text-neutral-500">
          Code sent to <span className="font-medium text-neutral-700">{email}</span>
        </p>

        <p className="text-center text-sm text-neutral-600">
          <button
            type="button"
            onClick={() => { setStep(1); setServerError(''); }}
            className="inline-flex items-center gap-1 font-medium text-brand-600 hover:text-brand-700 transition-colors"
          >
            <ArrowLeft size={14} />
            Change email
          </button>
        </p>
      </div>
    );
  }

  // Step 3: New password
  if (step === 3) {
    return (
      <form onSubmit={handleResetPassword} className="space-y-5" noValidate>
        <div className="text-center mb-2">
          <h2 className="text-lg font-semibold text-neutral-900">Set New Password</h2>
          <p className="text-sm text-neutral-500 mt-1">
            Create a strong new password for your account.
          </p>
        </div>

        {serverError && (
          <div className="p-3 rounded-lg bg-error-50 border border-red-200 text-sm text-error-700" role="alert">
            {serverError}
          </div>
        )}

        <Input
          label="New Password"
          name="newPassword"
          type={showPassword ? 'text' : 'password'}
          placeholder="Enter new password"
          value={newPassword}
          onChange={(e) => {
            setNewPassword(e.target.value);
            if (errors.newPassword) setErrors((prev) => ({ ...prev, newPassword: '' }));
          }}
          error={errors.newPassword}
          required
          leftIcon={<Lock size={18} />}
          rightIcon={
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="text-neutral-400 hover:text-neutral-600 transition-colors"
              aria-label={showPassword ? 'Hide password' : 'Show password'}
            >
              {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          }
          autoComplete="new-password"
        />

        <Input
          label="Confirm Password"
          name="confirmPassword"
          type={showConfirmPassword ? 'text' : 'password'}
          placeholder="Confirm new password"
          value={confirmPassword}
          onChange={(e) => {
            setConfirmPassword(e.target.value);
            if (errors.confirmPassword) setErrors((prev) => ({ ...prev, confirmPassword: '' }));
          }}
          error={errors.confirmPassword}
          required
          leftIcon={<Lock size={18} />}
          rightIcon={
            <button
              type="button"
              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              className="text-neutral-400 hover:text-neutral-600 transition-colors"
              aria-label={showConfirmPassword ? 'Hide password' : 'Show password'}
            >
              {showConfirmPassword ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          }
          autoComplete="new-password"
        />

        <Button type="submit" variant="primary" fullWidth loading={loading}>
          Reset Password
        </Button>
      </form>
    );
  }

  // Step 4: Success
  return (
    <div className="text-center space-y-5">
      <div className="w-16 h-16 bg-success-50 rounded-full flex items-center justify-center mx-auto">
        <CheckCircle size={32} className="text-success-600" />
      </div>
      <div>
        <h2 className="text-lg font-semibold text-neutral-900">Password Reset Successful</h2>
        <p className="text-sm text-neutral-500 mt-2">
          Your password has been changed. Please login with your new password.
        </p>
      </div>
      <Link
        to={ROUTES.LOGIN}
        className="inline-flex items-center justify-center w-full px-4 py-2.5 text-sm font-medium text-white bg-brand-600 rounded-lg hover:bg-brand-700 transition-colors"
      >
        Go to Login
      </Link>
    </div>
  );
}
