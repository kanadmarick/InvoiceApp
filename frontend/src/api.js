import axios from 'axios';

// In production (Nginx): VITE_API_URL is empty → relative URLs (same origin)
// In development: VITE_API_URL is not set → falls back to localhost:8000
const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true,
});

// Attach JWT access token to every request
api.interceptors.request.use((config) => {
  const tokens = JSON.parse(localStorage.getItem('tokens') || 'null');
  if (tokens?.access) {
    config.headers.Authorization = `Bearer ${tokens.access}`;
  }
  return config;
});

// On 401, try to refresh the token once
api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      const tokens = JSON.parse(localStorage.getItem('tokens') || 'null');
      if (tokens?.refresh) {
        try {
          const { data } = await axios.post(`${API_BASE}/accounts/token/refresh/`, {
            refresh: tokens.refresh,
          });
          localStorage.setItem(
            'tokens',
            JSON.stringify({ access: data.access, refresh: data.refresh || tokens.refresh })
          );
          original.headers.Authorization = `Bearer ${data.access}`;
          return api(original);
        } catch {
          localStorage.removeItem('tokens');
          localStorage.removeItem('user');
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

export default api;
