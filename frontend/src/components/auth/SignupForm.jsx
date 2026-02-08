import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Mail, Lock, Eye, EyeOff, User } from 'lucide-react';
import Input from '../common/Input';
import Button from '../common/Button';
import PasswordStrengthBar from '../common/PasswordStrengthBar';
import { validateEmail, validatePassword, validateConfirmPassword, validateName } from '../../utils/validators';
import { ROUTES } from '../../utils/constants';

/**
 * Signup form with client-side validation and password strength indicator.
 *
 * @param {function} onSubmit - Called with form data on valid submission
 * @param {boolean} loading
 * @param {string} serverError
 */
export default function SignupForm({ onSubmit, loading = false, serverError = '' }) {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [errors, setErrors] = useState({});
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: '' }));
    }
  };

  const validate = () => {
    const newErrors = {};
    const nameError = validateName(formData.name);
    const emailError = validateEmail(formData.email);
    const passwordError = validatePassword(formData.password);
    const confirmError = validateConfirmPassword(formData.password, formData.confirmPassword);

    if (nameError) newErrors.name = nameError;
    if (emailError) newErrors.email = emailError;
    if (passwordError) newErrors.password = passwordError;
    if (confirmError) newErrors.confirmPassword = confirmError;

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validate()) {
      onSubmit({
        name: formData.name,
        email: formData.email,
        password: formData.password,
      });
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5" noValidate>
      {serverError && (
        <div className="p-3 rounded-lg bg-error-50 border border-red-200 text-sm text-error-700" role="alert">
          {serverError}
        </div>
      )}

      <Input
        label="Full name"
        name="name"
        type="text"
        placeholder="John Doe"
        value={formData.name}
        onChange={handleChange}
        error={errors.name}
        required
        leftIcon={<User size={18} />}
        autoComplete="name"
      />

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

      <div>
        <Input
          label="Password"
          name="password"
          type={showPassword ? 'text' : 'password'}
          placeholder="Create a strong password"
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
          autoComplete="new-password"
        />
        <PasswordStrengthBar password={formData.password} />
      </div>

      <Input
        label="Confirm password"
        name="confirmPassword"
        type={showConfirmPassword ? 'text' : 'password'}
        placeholder="Re-enter your password"
        value={formData.confirmPassword}
        onChange={handleChange}
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
        Create account
      </Button>

      <p className="text-center text-sm text-neutral-600">
        Already have an account?{' '}
        <Link to={ROUTES.LOGIN} className="font-medium text-brand-600 hover:text-brand-700 transition-colors">
          Sign in
        </Link>
      </p>
    </form>
  );
}