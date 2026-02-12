import { createContext, useState, useEffect, useCallback, useMemo } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import api from '../api/axios';
import ENDPOINTS from '../api/endpoints';
import { getToken, setToken, removeToken, getUser, setUser as saveUser } from '../utils/storage';
import { ROUTES } from '../utils/constants';

/**
 * Authentication context.
 * Manages user session state, login, signup, OTP verification, and logout.
 * Provides auth state to the entire application tree.
 */
export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  /**
   * Initialize auth state on mount.
   * Checks for existing token and validates it by fetching user profile.
   */
  useEffect(() => {
    const initAuth = async () => {
      const token = getToken();
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const response = await api.get(ENDPOINTS.USER.PROFILE);
        const userData = response.data.user || response.data;
        setUser(userData);
        saveUser(userData);
        setIsAuthenticated(true);
      } catch (error) {
        // Token is invalid or expired — clean up
        removeToken();
        setUser(null);
        setIsAuthenticated(false);
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  /**
   * Login with email and password.
   * Stores token and user data on success.
   *
   * @param {object} credentials - { email, password, captchaToken }
   * @returns {Promise<{success: boolean, error?: string}>}
   */
  const login = useCallback(async (credentials) => {
    try {
      const response = await api.post(ENDPOINTS.AUTH.LOGIN, credentials);
      const { token, user: userData } = response.data;

      setToken(token);
      setUser(userData);
      saveUser(userData);
      setIsAuthenticated(true);

      // Redirect to the page user was trying to access, or dashboard
      const from = location.state?.from?.pathname || ROUTES.DASHBOARD;
      navigate(from, { replace: true });

      return { success: true };
    } catch (error) {
      const message =
        error.response?.data?.message ||
        error.response?.data?.error ||
        'Invalid credentials. Please try again.';
      return { success: false, error: message };
    }
  }, [navigate, location.state]);

  /**
   * Register a new user account.
   * Returns user data for OTP verification flow.
   *
   * @param {object} data - { name, email, password }
   * @returns {Promise<{success: boolean, error?: string, requiresOTP?: boolean}>}
   */
  const signup = useCallback(async (data) => {
    try {
      const response = await api.post(ENDPOINTS.AUTH.SIGNUP, data);
      return {
        success: true,
        requiresOTP: true,
        email: data.email,
        message: response.data.message || 'Verification code sent to your email.',
      };
    } catch (error) {
      const message =
        error.response?.data?.message ||
        error.response?.data?.error ||
        'Registration failed. Please try again.';
      return { success: false, error: message };
    }
  }, []);

  /**
   * Verify OTP after signup.
   * On success, stores token and redirects to dashboard.
   *
   * @param {string} email
   * @param {string} otp
   * @returns {Promise<{success: boolean, error?: string}>}
   */
  const verifyOTP = useCallback(async (email, otp) => {
    try {
      const response = await api.post(ENDPOINTS.AUTH.VERIFY_OTP, { email, otp });
      const { token, user: userData } = response.data;

      if (token) {
        setToken(token);
        setUser(userData);
        saveUser(userData);
        setIsAuthenticated(true);
        navigate(ROUTES.DASHBOARD, { replace: true });
      }

      return { success: true };
    } catch (error) {
      const message =
        error.response?.data?.message ||
        error.response?.data?.error ||
        'Invalid verification code. Please try again.';
      return { success: false, error: message };
    }
  }, [navigate]);

  /**
   * Resend OTP verification email.
   *
   * @param {string} email
   * @returns {Promise<{success: boolean, error?: string}>}
   */
  const resendOTP = useCallback(async (email) => {
    try {
      await api.post(ENDPOINTS.AUTH.VERIFY_OTP, { email, resend: true });
      return { success: true };
    } catch (error) {
      const message =
        error.response?.data?.message || 'Failed to resend code. Please try again.';
      return { success: false, error: message };
    }
  }, []);

  /**
   * Logout current session.
   * Clears all stored auth data and redirects to login.
   */
  const logout = useCallback(async () => {
    try {
      await api.post(ENDPOINTS.AUTH.LOGOUT);
    } catch {
      // Proceed with client-side logout even if API call fails
    } finally {
      removeToken();
      setUser(null);
      setIsAuthenticated(false);
      navigate(ROUTES.LOGIN, { replace: true });
    }
  }, [navigate]);

  /**
   * Logout from all sessions / devices.
   *
   * @returns {Promise<{success: boolean, error?: string}>}
   */
  const logoutAllSessions = useCallback(async () => {
    try {
      await api.post(ENDPOINTS.USER.LOGOUT_ALL);
      removeToken();
      setUser(null);
      setIsAuthenticated(false);
      navigate(ROUTES.LOGIN, { replace: true });
      return { success: true };
    } catch (error) {
      const message = error.response?.data?.message || 'Failed to logout from all sessions.';
      return { success: false, error: message };
    }
  }, [navigate]);

  /**
   * Update local user state after profile changes.
   * Does NOT call the API — use this after a successful API update.
   *
   * @param {object} updatedFields - Partial user data to merge
   */
  const updateUser = useCallback((updatedFields) => {
    setUser((prev) => {
      const updated = { ...prev, ...updatedFields };
      saveUser(updated);
      return updated;
    });
  }, []);

  // Memoize context value to prevent unnecessary re-renders
  const value = useMemo(
    () => ({
      user,
      loading,
      isAuthenticated,
      login,
      signup,
      verifyOTP,
      resendOTP,
      logout,
      logoutAllSessions,
      updateUser,
    }),
    [user, loading, isAuthenticated, login, signup, verifyOTP, resendOTP, logout, logoutAllSessions, updateUser]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}