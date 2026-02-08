import { useRef, useEffect } from 'react';
import MessageBubble from './MessageBubble';
import ChatInput from './ChatInput';
import EmptyState from '../common/EmptyState';
import { MessageSquare } from 'lucide-react';

/**
 * Chat interface for querying documents.
 * Displays message history and input.
 *
 * @param {Array} messages - Array of message objects { id, role, content, sources, status }
 * @param {function} onSend - Called with the message string
 * @param {boolean} loading - Shows loading indicator for pending response
 */
export default function ChatWindow({ messages = [], onSend, loading = false }) {
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex flex-col h-[calc(100vh-12rem)] bg-white rounded-xl border border-neutral-200 shadow-xs">
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-6 custom-scrollbar">
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center">
            <EmptyState
              icon={MessageSquare}
              title="Ask about your documents"
              description="Type a question below to retrieve verified information from your uploaded documents."
            />
          </div>
        ) : (
          <div className="space-y-6">
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}
            {loading && (
              <div className="flex items-center gap-3 text-neutral-500">
                <div className="flex gap-1">
                  <span className="w-2 h-2 bg-neutral-400 rounded-full animate-bounce [animation-delay:0ms]" />
                  <span className="w-2 h-2 bg-neutral-400 rounded-full animate-bounce [animation-delay:150ms]" />
                  <span className="w-2 h-2 bg-neutral-400 rounded-full animate-bounce [animation-delay:300ms]" />
                </div>
                <span className="text-sm">Retrieving information...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input area */}
      <div className="border-t border-neutral-200 p-4">
        <ChatInput onSend={onSend} disabled={loading} />
      </div>
    </div>
  );
}