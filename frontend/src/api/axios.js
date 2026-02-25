import axios from 'axios';
import { getToken, removeToken } from '../utils/storage';

/**
 * Configured Axios instance for all API communication.
 * Automatically attaches auth token and handles 401 responses.
 */
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: attach JWT token
api.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: handle auth errors globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const url = error.config?.url || '';
      // Don't redirect for auth endpoints — let the component handle the error
      const isAuthEndpoint = [
        '/login', '/signup', '/verify-otp',
        '/forgot-password', '/verify-reset-otp', '/reset-password'
      ].some((ep) => url.includes(ep));

      if (!isAuthEndpoint) {
        removeToken();
        // Notify auth context to clear state and redirect via React Router
        window.dispatchEvent(new Event('auth:session-expired'));
      }
    }
    return Promise.reject(error);
  }
);

export default api;