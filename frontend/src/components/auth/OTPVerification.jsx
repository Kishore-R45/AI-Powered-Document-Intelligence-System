import { useState, useRef, useEffect } from 'react';
import Button from '../common/Button';

/**
 * OTP input component with individual digit inputs.
 * Auto-focuses next input and supports paste.
 *
 * @param {function} onVerify - Called with the complete OTP string
 * @param {function} onResend - Called when user requests a new OTP
 * @param {boolean} loading
 * @param {string} error
 */
export default function OTPVerification({ onVerify, onResend, loading = false, error = '' }) {
  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const inputRefs = useRef([]);

  useEffect(() => {
    inputRefs.current[0]?.focus();
  }, []);

  const handleChange = (index, value) => {
    if (!/^\d?$/.test(value)) return; // Only allow single digits

    const newOtp = [...otp];
    newOtp[index] = value;
    setOtp(newOtp);

    // Auto-focus next input
    if (value && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (index, e) => {
    // Move to previous input on backspace
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handlePaste = (e) => {
    e.preventDefault();
    const pasted = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6);
    if (pasted.length === 6) {
      const newOtp = pasted.split('');
      setOtp(newOtp);
      inputRefs.current[5]?.focus();
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const otpString = otp.join('');
    if (otpString.length === 6) {
      onVerify(otpString);
    }
  };

  const isComplete = otp.every((digit) => digit !== '');

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="text-center">
        <h3 className="text-lg font-semibold text-neutral-900 mb-1">Verify your email</h3>
        <p className="text-sm text-neutral-500">
          We've sent a 6-digit verification code to your email address.
        </p>
      </div>

      {error && (
        <div className="p-3 rounded-lg bg-error-50 border border-red-200 text-sm text-error-700 text-center" role="alert">
          {error}
        </div>
      )}

      {/* OTP digit inputs */}
      <div className="flex justify-center gap-3" onPaste={handlePaste}>
        {otp.map((digit, index) => (
          <input
            key={index}
            ref={(el) => (inputRefs.current[index] = el)}
            type="text"
            inputMode="numeric"
            maxLength={1}
            value={digit}
            onChange={(e) => handleChange(index, e.target.value)}
            onKeyDown={(e) => handleKeyDown(index, e)}
            className="w-12 h-14 text-center text-xl font-semibold border border-neutral-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500 outline-none transition-colors"
            aria-label={`Digit ${index + 1}`}
          />
        ))}
      </div>

      <Button type="submit" variant="primary" fullWidth disabled={!isComplete} loading={loading}>
        Verify
      </Button>

      <p className="text-center text-sm text-neutral-500">
        Didn't receive a code?{' '}
        <button
          type="button"
          onClick={onResend}
          className="font-medium text-brand-600 hover:text-brand-700 transition-colors"
        >
          Resend
        </button>
      </p>
    </form>
  );
}