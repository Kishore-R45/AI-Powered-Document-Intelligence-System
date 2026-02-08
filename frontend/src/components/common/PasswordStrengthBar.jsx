import { clsx } from 'clsx';
import { getPasswordStrength, PASSWORD_STRENGTH_LABELS, PASSWORD_STRENGTH_COLORS } from '../../utils/validators';

/**
 * Visual password strength indicator.
 * Shows a segmented bar and descriptive label.
 */
export default function PasswordStrengthBar({ password }) {
  const strength = getPasswordStrength(password);

  if (!password) return null;

  return (
    <div className="mt-2">
      <div className="flex gap-1 mb-1">
        {[1, 2, 3, 4].map((level) => (
          <div
            key={level}
            className={clsx(
              'h-1.5 flex-1 rounded-full transition-colors duration-300',
              level <= strength
                ? PASSWORD_STRENGTH_COLORS[strength]
                : 'bg-neutral-200'
            )}
          />
        ))}
      </div>
      <p className={clsx(
        'text-xs font-medium',
        strength <= 1 ? 'text-error-500' :
        strength === 2 ? 'text-warning-500' :
        strength === 3 ? 'text-brand-500' :
        'text-success-500'
      )}>
        {PASSWORD_STRENGTH_LABELS[strength]}
      </p>
    </div>
  );
}