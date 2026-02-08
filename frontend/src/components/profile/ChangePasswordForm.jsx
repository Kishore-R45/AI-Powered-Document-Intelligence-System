import { useState } from 'react';
import { Lock, Eye, EyeOff } from 'lucide-react';
import Card from '../common/Card';
import Input from '../common/Input';
import Button from '../common/Button';
import PasswordStrengthBar from '../common/PasswordStrengthBar';
import { validatePassword, validateConfirmPassword } from '../../utils/validators';

/**
 * Change password form with validation and strength indicator.
 *
 * @param {function} onSubmit - Called with { currentPassword, newPassword }
 * @param {boolean} loading
 * @param {string} error
 * @param {string} success
 */
export default function ChangePasswordForm({ onSubmit, loading = false, error = '', success = '' }) {
  const [formData, setFormData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmNewPassword: '',
  });
  const [errors, setErrors] = useState({});
  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false,
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: '' }));
    }
  };

  const toggleShow = (field) => {
    setShowPasswords((prev) => ({ ...prev, [field]: !prev[field] }));
  };

  const validate = () => {
    const newErrors = {};
    if (!formData.currentPassword) newErrors.currentPassword = 'Current password is required';
    const newPwError = validatePassword(formData.newPassword);
    if (newPwError) newErrors.newPassword = newPwError;
    const confirmError = validateConfirmPassword(formData.newPassword, formData.confirmNewPassword);
    if (confirmError) newErrors.confirmNewPassword = confirmError;
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validate()) {
      onSubmit({
        currentPassword: formData.currentPassword,
        newPassword: formData.newPassword,
      });
    }
  };

  return (
    <Card>
      <h3 className="text-base font-semibold text-neutral-900 mb-6">Change Password</h3>
      <form onSubmit={handleSubmit} className="space-y-5" noValidate>
        {error && (
          <div className="p-3 rounded-lg bg-error-50 border border-red-200 text-sm text-error-700" role="alert">
            {error}
          </div>
        )}
        {success && (
          <div className="p-3 rounded-lg bg-success-50 border border-green-200 text-sm text-success-700" role="status">
            {success}
          </div>
        )}

        <Input
          label="Current password"
          name="currentPassword"
          type={showPasswords.current ? 'text' : 'password'}
          value={formData.currentPassword}
          onChange={handleChange}
          error={errors.currentPassword}
          required
          leftIcon={<Lock size={18} />}
          rightIcon={
            <button type="button" onClick={() => toggleShow('current')} className="text-neutral-400 hover:text-neutral-600" aria-label="Toggle visibility">
              {showPasswords.current ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          }
          autoComplete="current-password"
        />

        <div>
          <Input
            label="New password"
            name="newPassword"
            type={showPasswords.new ? 'text' : 'password'}
            value={formData.newPassword}
            onChange={handleChange}
            error={errors.newPassword}
            required
            leftIcon={<Lock size={18} />}
            rightIcon={
              <button type="button" onClick={() => toggleShow('new')} className="text-neutral-400 hover:text-neutral-600" aria-label="Toggle visibility">
                {showPasswords.new ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            }
            autoComplete="new-password"
          />
          <PasswordStrengthBar password={formData.newPassword} />
        </div>

        <Input
          label="Confirm new password"
          name="confirmNewPassword"
          type={showPasswords.confirm ? 'text' : 'password'}
          value={formData.confirmNewPassword}
          onChange={handleChange}
          error={errors.confirmNewPassword}
          required
          leftIcon={<Lock size={18} />}
          rightIcon={
            <button type="button" onClick={() => toggleShow('confirm')} className="text-neutral-400 hover:text-neutral-600" aria-label="Toggle visibility">
              {showPasswords.confirm ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          }
          autoComplete="new-password"
        />

        <Button type="submit" variant="primary" loading={loading}>
          Update Password
        </Button>
      </form>
    </Card>
  );
}