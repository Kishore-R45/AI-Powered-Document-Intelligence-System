import { useState } from 'react';
import { Calendar } from 'lucide-react';
import Input from '../common/Input';
import { clsx } from 'clsx';

/**
 * Toggle for document expiry date.
 * When enabled, shows a date input.
 *
 * @param {boolean} hasExpiry - Whether expiry is enabled
 * @param {function} onToggle - Called with boolean
 * @param {string} expiryDate - ISO date string
 * @param {function} onDateChange - Called with date string
 */
export default function ExpiryToggle({ hasExpiry, onToggle, expiryDate, onDateChange }) {
  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <label className="text-sm font-medium text-neutral-700">
          Has expiry date?
        </label>
        <button
          type="button"
          role="switch"
          aria-checked={hasExpiry}
          onClick={() => onToggle(!hasExpiry)}
          className={clsx(
            'relative w-11 h-6 rounded-full transition-colors duration-200 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-500',
            hasExpiry ? 'bg-brand-600' : 'bg-neutral-300'
          )}
        >
          <span
            className={clsx(
              'absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow-sm transition-transform duration-200',
              hasExpiry && 'translate-x-5'
            )}
          />
        </button>
      </div>
      {hasExpiry && (
        <div className="animate-slide-up">
          <Input
            label="Expiry date"
            type="date"
            value={expiryDate}
            onChange={(e) => onDateChange(e.target.value)}
            leftIcon={<Calendar size={18} />}
            required
            min={new Date().toISOString().split('T')[0]}
          />
        </div>
      )}
    </div>
  );
}