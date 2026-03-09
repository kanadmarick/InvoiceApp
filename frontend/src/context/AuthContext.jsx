import { createContext, useContext, useState, useEffect } from 'react';
import api from '../api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() =>
    JSON.parse(localStorage.getItem('user') || 'null')
  );
  const [loading, setLoading] = useState(false);

  const isAuthenticated = !!user;

  async function login(username, password) {
    const { data } = await api.post('/accounts/login/', { username, password });
    localStorage.setItem('tokens', JSON.stringify(data.tokens));
    localStorage.setItem('user', JSON.stringify(data.user));
    setUser(data.user);
    return data;
  }

  async function guestLogin() {
    const { data } = await api.post('/accounts/guest-login/');
    localStorage.setItem('tokens', JSON.stringify(data.tokens));
    localStorage.setItem('user', JSON.stringify(data.user));
    setUser(data.user);
    return data;
  }

  async function register(payload) {
    const { data } = await api.post('/accounts/register/', payload);
    localStorage.setItem('tokens', JSON.stringify(data.tokens));
    localStorage.setItem('user', JSON.stringify(data.user));
    setUser(data.user);
    return data;
  }

  async function logout() {
    try {
      const tokens = JSON.parse(localStorage.getItem('tokens') || 'null');
      if (tokens?.refresh) {
        await api.post('/accounts/logout/', { refresh: tokens.refresh });
      }
    } catch {
      // ignore
    }
    localStorage.removeItem('tokens');
    localStorage.removeItem('user');
    setUser(null);
  }

  function updateUser(updatedUser) {
    localStorage.setItem('user', JSON.stringify(updatedUser));
    setUser(updatedUser);
  }

  return (
    <AuthContext.Provider
      value={{ user, isAuthenticated, loading, login, guestLogin, register, logout, updateUser }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
