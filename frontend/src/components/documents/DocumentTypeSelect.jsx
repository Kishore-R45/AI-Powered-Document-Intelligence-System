import { DOCUMENT_TYPES } from '../../utils/constants';
import { clsx } from 'clsx';
import { FileText, Shield, GraduationCap, CreditCard, Heart, FolderOpen } from 'lucide-react';

/**
 * Document type selector using card-based selection.
 *
 * @param {string} value - Currently selected document type
 * @param {function} onChange - Called with the selected type value
 */

const typeIcons = {
  insurance: Shield,
  academic: GraduationCap,
  id: CreditCard,
  financial: CreditCard,
  medical: Heart,
  general: FolderOpen,
};

export default function DocumentTypeSelect({ value, onChange }) {
  return (
    <div>
      <label className="block text-sm font-medium text-neutral-700 mb-3">
        Document type <span className="text-error-500">*</span>
      </label>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
        {DOCUMENT_TYPES.map((type) => {
          const Icon = typeIcons[type.value] || FileText;
          const isSelected = value === type.value;
          return (
            <button
              key={type.value}
              type="button"
              onClick={() => onChange(type.value)}
              className={clsx(
                'flex flex-col items-center gap-2 p-4 rounded-lg border-2 transition-all duration-200 text-center',
                isSelected
                  ? 'border-brand-500 bg-brand-50 text-brand-700'
                  : 'border-neutral-200 hover:border-neutral-300 hover:bg-neutral-25 text-neutral-600'
              )}
              aria-pressed={isSelected}
            >
              <Icon size={22} />
              <span className="text-sm font-medium">{type.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}