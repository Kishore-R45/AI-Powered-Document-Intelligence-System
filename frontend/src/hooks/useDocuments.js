import { useState, useCallback, useEffect } from 'react';
import api from '../api/axios';
import ENDPOINTS from '../api/endpoints';

/**
 * Hook for managing document operations.
 * Provides document list fetching, upload, and deletion with loading/error states.
 *
 * @returns {{
 *   documents: Array,
 *   loading: boolean,
 *   uploading: boolean,
 *   uploadProgress: number,
 *   error: string,
 *   fetchDocuments: () => Promise,
 *   uploadDocument: (file: File, metadata: object) => Promise,
 *   deleteDocument: (id: string) => Promise,
 *   clearError: () => void,
 * }}
 */
export default function useDocuments() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState('');

  /**
   * Fetch all documents for the current user.
   */
  const fetchDocuments = useCallback(async () => {
    try {
      setLoading(true);
      setError('');
      const response = await api.get(ENDPOINTS.DOCUMENTS.LIST);
      const data = response.data.documents || response.data || [];
      setDocuments(data);
    } catch (err) {
      const message = err.response?.data?.message || 'Failed to load documents.';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Upload a document with metadata.
   * Tracks upload progress for the progress indicator.
   *
   * @param {File} file - The file to upload
   * @param {object} metadata - { name?, type, hasExpiry, expiryDate? }
   * @returns {Promise<{success: boolean, document?: object, error?: string}>}
   */
  const uploadDocument = useCallback(async (file, metadata) => {
    try {
      setUploading(true);
      setUploadProgress(0);
      setError('');

      const formData = new FormData();
      formData.append('file', file);
      formData.append('type', metadata.type);

      if (metadata.name) {
        formData.append('name', metadata.name);
      }
      if (metadata.hasExpiry && metadata.expiryDate) {
        formData.append('hasExpiry', 'true');
        formData.append('expiryDate', metadata.expiryDate);
      }

      const response = await api.post(ENDPOINTS.DOCUMENTS.UPLOAD, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent) => {
          const percent = Math.round(
            (progressEvent.loaded * 100) / (progressEvent.total || 1)
          );
          setUploadProgress(percent);
        },
      });

      const newDocument = response.data.document || response.data;

      // Add the new document to the local list
      setDocuments((prev) => [newDocument, ...prev]);

      return { success: true, document: newDocument };
    } catch (err) {
      const message = err.response?.data?.message || 'Failed to upload document.';
      setError(message);
      return { success: false, error: message };
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  }, []);

  /**
   * Delete a document by ID.
   *
   * @param {string} documentId
   * @returns {Promise<{success: boolean, error?: string}>}
   */
  const deleteDocument = useCallback(async (documentId) => {
    // Store previous state for rollback
    const previousDocuments = [...documents];

    try {
      // Optimistic removal
      setDocuments((prev) => prev.filter((doc) => doc.id !== documentId));

      await api.delete(ENDPOINTS.DOCUMENTS.DELETE(documentId));

      return { success: true };
    } catch (err) {
      // Rollback on failure
      setDocuments(previousDocuments);
      const message = err.response?.data?.message || 'Failed to delete document.';
      setError(message);
      return { success: false, error: message };
    }
  }, [documents]);

  /**
   * Clear the current error state.
   */
  const clearError = useCallback(() => {
    setError('');
  }, []);

  return {
    documents,
    loading,
    uploading,
    uploadProgress,
    error,
    fetchDocuments,
    uploadDocument,
    deleteDocument,
    clearError,
  };
}