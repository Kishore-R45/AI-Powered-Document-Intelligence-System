import { useEffect } from 'react';
import { Trash2, MessageSquare } from 'lucide-react';
import ChatWindow from '../components/chat/ChatWindow';
import Button from '../components/common/Button';
import useChat from '../hooks/useChat';
import { QUERY_STATUS } from '../utils/constants';

/**
 * Chat / Document Query page.
 * Provides a conversational interface to ask questions about uploaded documents.
 */
export default function ChatPage() {
  const { messages, status, sendQuery, loadHistory, clearMessages } = useChat();

  /**
   * Load previous chat history on mount.
   */
  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  const isLoading = status === QUERY_STATUS.LOADING;

  return (
    <div className="flex flex-col h-full animate-fade-in">
      {/* Page header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-3">
        <div>
          <h1 className="page-heading flex items-center gap-2">
            <MessageSquare size={24} className="text-brand-600" />
            Query Documents
          </h1>
          <p className="page-subheading">
            Ask questions about your uploaded documents and get verified, source-referenced answers.
          </p>
        </div>
        {messages.length > 0 && (
          <Button
            variant="outline"
            size="sm"
            leftIcon={<Trash2 size={14} />}
            onClick={clearMessages}
            disabled={isLoading}
          >
            Clear Chat
          </Button>
        )}
      </div>

      {/* Disclaimer */}
      <div className="px-4 py-2.5 bg-brand-50 border border-brand-200 rounded-lg mb-3 flex-shrink-0">
        <p className="text-xs text-brand-700">
          <span className="font-semibold">Note:</span> All answers are sourced exclusively from your uploaded documents.
          If the requested information is not found, you will be clearly informed.
        </p>
      </div>

      {/* Chat window */}
      <div className="flex-1 min-h-0">
        <ChatWindow
          messages={messages}
          onSend={sendQuery}
          loading={isLoading}
        />
      </div>
    </div>
  );
}