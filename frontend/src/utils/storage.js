/**
 * Secure token storage abstraction.
 * Centralizes token access so the storage mechanism can be changed
 * (e.g., from localStorage to HTTP-only cookies) without modifying consumers.
 */

const TOKEN_KEY = 'info_vault_token';
const USER_KEY = 'info_vault_user';

export const getToken = () => {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
};

export const setToken = (token) => {
  try {
    localStorage.setItem(TOKEN_KEY, token);
  } catch {
    // Silent fail - storage may be unavailable
  }
};

export const removeToken = () => {
  try {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  } catch {
    // Silent fail
  }
};

export const getUser = () => {
  try {
    const user = localStorage.getItem(USER_KEY);
    return user ? JSON.parse(user) : null;
  } catch {
    return null;
  }
};

export const setUser = (user) => {
  try {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  } catch {
    // Silent fail
  }
};