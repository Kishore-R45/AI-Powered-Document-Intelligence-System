/**
 * Application-wide constants.
 */

export const APP_NAME = import.meta.env.VITE_APP_NAME || 'Info Vault';

export const DOCUMENT_TYPES = [
  { value: 'insurance', label: 'Insurance', description: 'Health, auto, life insurance documents' },
  { value: 'academic', label: 'Academic', description: 'Transcripts, diplomas, certificates' },
  { value: 'id', label: 'Identification', description: 'Passport, driver\'s license, national ID' },
  { value: 'financial', label: 'Financial', description: 'Tax documents, bank statements' },
  { value: 'medical', label: 'Medical', description: 'Medical records, prescriptions' },
  { value: 'general', label: 'General Document', description: 'Any other personal document' },
];

export const ACCEPTED_FILE_TYPES = {
  'application/pdf': ['.pdf'],
  'image/jpeg': ['.jpg', '.jpeg'],
  'image/png': ['.png'],
  'image/webp': ['.webp'],
};

export const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  SIGNUP: '/signup',
  FORGOT_PASSWORD: '/forgot-password',
  DASHBOARD: '/dashboard',
  UPLOAD: '/upload',
  DOCUMENTS: '/documents',
  CHAT: '/chat',
  PROFILE: '/profile',
  NOTIFICATIONS: '/notifications',
};

export const QUERY_STATUS = {
  IDLE: 'idle',
  LOADING: 'loading',
  SUCCESS: 'success',
  ERROR: 'error',
  NOT_FOUND: 'not_found',
};