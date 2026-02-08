import { useState, useCallback } from 'react';
import api from '../api/axios';
import ENDPOINTS from '../api/endpoints';
import { QUERY_STATUS } from '../utils/constants';

/**
 * Hook for managing the document query chat interface.
 * Handles message history, sending queries, and processing responses.
 *
 * @returns {{
 *   messages: Array,
 *   status: string,
 *   sendQuery: (question: string) => Promise,
 *   clearMessages: () => void,
 * }}
 */

let messageIdCounter = 0;

/**
 * Generate a unique local message ID.
 */
const generateId = () => `msg_${Date.now()}_${++messageIdCounter}`;

export default function useChat() {
  const [messages, setMessages] = useState([]);
  const [status, setStatus] = useState(QUERY_STATUS.IDLE);

  /**
   * Send a user query to the backend.
   * Adds the user message immediately, then appends the AI response.
   *
   * @param {string} question - The user's question
   * @returns {Promise<void>}
   */
  const sendQuery = useCallback(async (question) => {
    // Add user message to chat
    const userMessage = {
      id: generateId(),
      role: 'user',
      content: question,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setStatus(QUERY_STATUS.LOADING);

    try {
      const response = await api.post(ENDPOINTS.CHAT.QUERY, { question });
      const data = response.data;

      /**
       * Expected response shape from backend:
       * {
       *   answer: string,
       *   found: boolean,
       *   sources: [{ documentName: string, page?: number }]
       * }
       */
      const assistantMessage = {
        id: generateId(),
        role: 'assistant',
        content: data.answer || data.response || 'No response received.',
        sources: data.sources || [],
        status: data.found === false ? QUERY_STATUS.NOT_FOUND : QUERY_STATUS.SUCCESS,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setStatus(data.found === false ? QUERY_STATUS.NOT_FOUND : QUERY_STATUS.SUCCESS);
    } catch (error) {
      const errorMessage = {
        id: generateId(),
        role: 'assistant',
        content:
          error.response?.data?.message ||
          'Unable to process your query. Please try again.',
        sources: [],
        status: QUERY_STATUS.ERROR,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, errorMessage]);
      setStatus(QUERY_STATUS.ERROR);
    }
  }, []);

  /**
   * Load previous chat history from the backend.
   *
   * @returns {Promise<void>}
   */
  const loadHistory = useCallback(async () => {
    try {
      setStatus(QUERY_STATUS.LOADING);
      const response = await api.get(ENDPOINTS.CHAT.HISTORY);
      const history = response.data.messages || response.data || [];
      setMessages(history);
      setStatus(QUERY_STATUS.IDLE);
    } catch (error) {
      // Silently fail — history is non-critical
      console.error('Failed to load chat history:', error);
      setStatus(QUERY_STATUS.IDLE);
    }
  }, []);

  /**
   * Clear all messages from the chat.
   */
  const clearMessages = useCallback(() => {
    setMessages([]);
    setStatus(QUERY_STATUS.IDLE);
  }, []);

  return {
    messages,
    status,
    sendQuery,
    loadHistory,
    clearMessages,
  };
}