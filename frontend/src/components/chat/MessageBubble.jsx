import { clsx } from 'clsx';
import { User, Shield, AlertCircle } from 'lucide-react';
import SourceReference from './SourceReference';

/**
 * Individual message bubble in the chat interface.
 *
 * @param {object} message - { id, role: 'user'|'assistant', content, sources, status }
 */
export default function MessageBubble({ message }) {
  const isUser = message.role === 'user';
  const isNotFound = message.status === 'not_found';

  return (
    <div className={clsx('flex gap-3', isUser ? 'justify-end' : 'justify-start')}>
      {/* Avatar */}
      {!isUser && (
        <div className="w-8 h-8 bg-brand-100 rounded-full flex items-center justify-center shrink-0">
          <Shield size={16} className="text-brand-600" />
        </div>
      )}

      <div className={clsx('max-w-[75%]', isUser && 'order-first')}>
        {/* Message content */}
        <div
          className={clsx(
            'rounded-xl px-4 py-3 text-sm',
            isUser
              ? 'bg-brand-600 text-white rounded-br-sm'
              : isNotFound
                ? 'bg-warning-50 border border-warning-200 text-neutral-800 rounded-bl-sm'
                : 'bg-neutral-100 text-neutral-900 rounded-bl-sm'
          )}
        >
          {isNotFound && (
            <div className="flex items-center gap-2 mb-2 text-warning-700">
              <AlertCircle size={16} />
              <span className="text-xs font-semibold uppercase tracking-wide">Not found in documents</span>
            </div>
          )}
          <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
        </div>

        {/* Source references */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="mt-2">
            <SourceReference sources={message.sources} />
          </div>
        )}
      </div>

      {/* User avatar */}
      {isUser && (
        <div className="w-8 h-8 bg-neutral-200 rounded-full flex items-center justify-center shrink-0">
          <User size={16} className="text-neutral-600" />
        </div>
      )}
    </div>
  );
}