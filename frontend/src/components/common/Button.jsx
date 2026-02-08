import { clsx } from 'clsx';
import Spinner from './Spinner';

/**
 * Reusable Button component.
 * Supports multiple variants, sizes, loading state, and icon placement.
 *
 * @param {'primary'|'secondary'|'outline'|'ghost'|'danger'} variant
 * @param {'sm'|'md'|'lg'} size
 * @param {boolean} loading - Shows spinner and disables interaction
 * @param {React.ReactNode} leftIcon - Icon before text
 * @param {React.ReactNode} rightIcon - Icon after text
 * @param {boolean} fullWidth - Stretches to container width
 */
export default function Button({
  children,
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled = false,
  leftIcon,
  rightIcon,
  fullWidth = false,
  className = '',
  type = 'button',
  ...props
}) {
  const baseStyles = 'inline-flex items-center justify-center font-medium rounded-lg transition-all duration-200 focus-visible:outline-2 focus-visible:outline-offset-2 disabled:cursor-not-allowed';

  const variants = {
    primary: 'bg-brand-600 text-white hover:bg-brand-700 active:bg-brand-800 focus-visible:outline-brand-600 disabled:bg-brand-300',
    secondary: 'bg-brand-50 text-brand-700 hover:bg-brand-100 active:bg-brand-200 focus-visible:outline-brand-600 disabled:bg-neutral-100 disabled:text-neutral-400',
    outline: 'border border-neutral-300 bg-white text-neutral-700 hover:bg-neutral-50 active:bg-neutral-100 focus-visible:outline-brand-600 disabled:bg-neutral-50 disabled:text-neutral-400',
    ghost: 'text-neutral-600 hover:bg-neutral-100 active:bg-neutral-200 focus-visible:outline-brand-600 disabled:text-neutral-400',
    danger: 'bg-error-500 text-white hover:bg-red-600 active:bg-red-700 focus-visible:outline-error-500 disabled:bg-red-300',
  };

  const sizes = {
    sm: 'text-sm px-3 py-1.5 gap-1.5',
    md: 'text-sm px-4 py-2.5 gap-2',
    lg: 'text-base px-5 py-3 gap-2',
  };

  return (
    <button
      type={type}
      disabled={disabled || loading}
      className={clsx(
        baseStyles,
        variants[variant],
        sizes[size],
        fullWidth && 'w-full',
        className
      )}
      {...props}
    >
      {loading ? (
        <Spinner size="sm" />
      ) : (
        leftIcon && <span className="shrink-0">{leftIcon}</span>
      )}
      {children}
      {!loading && rightIcon && <span className="shrink-0">{rightIcon}</span>}
    </button>
  );
}