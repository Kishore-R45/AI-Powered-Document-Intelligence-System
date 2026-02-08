import { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';

/**
 * Convenience hook for accessing auth context.
 * Throws an error if used outside of AuthProvider.
 *
 * @returns {{
 *   user: object|null,
 *   loading: boolean,
 *   isAuthenticated: boolean,
 *   login: (email: string, password: string) => Promise,
 *   signup: (data: object) => Promise,
 *   verifyOTP: (email: string, otp: string) => Promise,
 *   resendOTP: (email: string) => Promise,
 *   logout: () => Promise,
 *   logoutAllSessions: () => Promise,
 *   updateUser: (fields: object) => void,
 * }}
 */
export default function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error(
      'useAuth must be used within an AuthProvider. ' +
      'Wrap your component tree with <AuthProvider>.'
    );
  }

  return context;
}