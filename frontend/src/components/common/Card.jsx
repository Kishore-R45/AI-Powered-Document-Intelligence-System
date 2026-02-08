import { clsx } from 'clsx';

/**
 * Reusable card container with optional hover effect and padding variants.
 */
export default function Card({
  children,
  className = '',
  hover = false,
  padding = 'md',
  ...props
}) {
  const paddings = {
    none: '',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  };

  return (
    <div
      className={clsx(
        'bg-white rounded-xl border border-neutral-200 shadow-xs',
        hover && 'hover:shadow-md hover:border-neutral-300 transition-all duration-200',
        paddings[padding],
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}