import { useState, useRef } from 'react';
import { Link } from 'react-router-dom';
import { Mail, Lock, Eye, EyeOff } from 'lucide-react';
import Input from '../common/Input';
import Button from '../common/Button';
import ReCaptcha from '../common/ReCaptcha';
import { validateEmail, validatePassword } from '../../utils/validators';
import { ROUTES } from '../../utils/constants';

/**
 * Login form component with client-side validation and error handling.
 *
 * @param {function} onSubmit - Called with { email, password } on valid submission
 * @param {boolean} loading - Disables form during submission
 * @param {string} serverError - Error message from API
 */
export default function LoginForm({ onSubmit, loading = false, serverError = '' }) {
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [errors, setErrors] = useState({});
  const [showPassword, setShowPassword] = useState(false);
  const [captchaToken, setCaptchaToken] = useState('');
  const recaptchaRef = useRef(null);

  // Skip captcha on localhost (Google reCAPTCHA doesn't support localhost)
  const isLocalhost = ['localhost', '127.0.0.1', '0.0.0.0'].includes(window.location.hostname);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    // Clear field error on change
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: '' }));
    }
  };

  const validate = () => {
    const newErrors = {};
    const emailError = validateEmail(formData.email);
    const passwordError = formData.password ? '' : 'Password is required';
    if (emailError) newErrors.email = emailError;
    if (passwordError) newErrors.password = passwordError;
    if (!isLocalhost && !captchaToken) newErrors.captcha = 'Please complete the captcha';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validate()) {
      onSubmit({ ...formData, captchaToken: isLocalhost ? 'localhost-bypass' : captchaToken });
    }
  };
  
  const handleCaptchaChange = (token) => {
    setCaptchaToken(token);
    if (errors.captcha) {
      setErrors((prev) => ({ ...prev, captcha: '' }));
    }
  };
  
  const handleCaptchaExpired = () => {
    setCaptchaToken('');
    setErrors((prev) => ({ ...prev, captcha: 'Captcha expired. Please verify again.' }));
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5" noValidate>
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
        value={formData.email}
        onChange={handleChange}
        error={errors.email}
        required
        leftIcon={<Mail size={18} />}
        autoComplete="email"
      />

      <Input
        label="Password"
        name="password"
        type={showPassword ? 'text' : 'password'}
        placeholder="Enter your password"
        value={formData.password}
        onChange={handleChange}
        error={errors.password}
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
        autoComplete="current-password"
      />

      {/* reCAPTCHA - hidden on localhost */}
      {!isLocalhost && (
        <div>
          <ReCaptcha
            ref={recaptchaRef}
            onChange={handleCaptchaChange}
            onExpired={handleCaptchaExpired}
          />
          {errors.captcha && (
            <p className="mt-1 text-sm text-error-600">{errors.captcha}</p>
          )}
        </div>
      )}

      <Button type="submit" variant="primary" fullWidth loading={loading}>
        Sign in
      </Button>

      <p className="text-center text-sm text-neutral-600">
        Don't have an account?{' '}
        <Link to={ROUTES.SIGNUP} className="font-medium text-brand-600 hover:text-brand-700 transition-colors">
          Sign up
        </Link>
      </p>
    </form>
  );
}