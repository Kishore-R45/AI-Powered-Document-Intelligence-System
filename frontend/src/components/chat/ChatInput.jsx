import { useState } from 'react';
import { Send } from 'lucide-react';
import { clsx } from 'clsx';

/**
 * Chat message input with send button.
 * Supports Enter to send and Shift+Enter for new line.
 *
 * @param {function} onSend - Called with the message string
 * @param {boolean} disabled - Disables input during loading
 */
export default function ChatInput({ onSend, disabled = false }) {
  const [message, setMessage] = useState('');

  const handleSubmit = () => {
    const trimmed = message.trim();
    if (trimmed && !disabled) {
      onSend(trimmed);
      setMessage('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="flex items-end gap-3">
      <textarea
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask a question about your documents..."
        rows={1}
        disabled={disabled}
        className={clsx(
          'flex-1 resize-none rounded-lg border border-neutral-300 bg-white px-4 py-3 text-sm',
          'placeholder:text-neutral-400 focus:ring-2 focus:ring-brand-500 focus:border-brand-500 outline-none',
          'disabled:bg-neutral-50 disabled:cursor-not-allowed',
          'max-h-32'
        )}
        style={{ minHeight: '44px' }}
        aria-label="Type your question"
      />
      <button
        onClick={handleSubmit}
        disabled={disabled || !message.trim()}
        className={clsx(
          'p-3 rounded-lg transition-colors duration-200 shrink-0',
          message.trim() && !disabled
            ? 'bg-brand-600 text-white hover:bg-brand-700'
            : 'bg-neutral-100 text-neutral-400 cursor-not-allowed'
        )}
        aria-label="Send message"
      >
        <Send size={18} />
      </button>
    </div>
  );
}