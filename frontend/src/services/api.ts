import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 globally - redirect to login (except on login/register endpoints)
api.interceptors.response.use(
  (res) => res,
  (err) => {
    const url = err.config?.url || '';
    if (err.response?.status === 401 && !url.includes('/login') && !url.includes('/register')) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(err);
  }
);

// ---- Auth ----
export const authApi = {
  register: (data: { name: string; email: string; password: string; phone_number?: string }) =>
    api.post('/api/auth/register', data),
  login: (email: string, password: string) =>
    api.post('/api/auth/login/json', { email, password }),
  getMe: () => api.get('/api/auth/me'),
  updateMe: (data: Partial<{ name: string; phone_number: string; email_notifications: boolean; push_notifications: boolean; sms_notifications: boolean }>) =>
    api.put('/api/auth/me', data),
  changePassword: (old_password: string, new_password: string) =>
    api.post(`/api/auth/change-password?old_password=${old_password}&new_password=${new_password}`),
};

// ---- Products ----
export const productsApi = {
  add: (data: { product_url: string; target_min_price?: number; target_max_price?: number }) =>
    api.post('/api/products', data),
  resolveUrl: (product_url: string) =>
    api.post('/api/products/resolve-url', { product_url }),
  list: (params?: { platform?: string; search?: string; status_filter?: string }) =>
    api.get('/api/products', { params }),
  get: (id: number) => api.get(`/api/products/${id}`),
  getDetail: (trackerId: number) => api.get(`/api/products/${trackerId}/detail`),
  getPrices: (productId: number) => api.get(`/api/products/${productId}/prices`),
  getPriceHistory: (productId: number, store: string = 'all', period: string = 'all') =>
    api.get(`/api/products/${productId}/price-history`, { params: { store, period } }),
  getComparison: (productId: number) => api.get(`/api/products/${productId}/comparison`),
  getStatistics: (productId: number) => api.get(`/api/products/${productId}/statistics`),
  track: (productId: number, data?: object) => api.post(`/api/products/${productId}/track`, data),
  setAlert: (productId: number, data: object) => api.post(`/api/products/${productId}/alert`, data),
  update: (id: number, data: object) => api.put(`/api/products/${id}`, data),
  delete: (id: number) => api.delete(`/api/products/${id}`),
  pause: (id: number) => api.post(`/api/products/${id}/pause`),
  resume: (id: number) => api.post(`/api/products/${id}/resume`),
  history: (productId: number, period: string = 'all') =>
    api.get(`/api/products/${productId}/history`, { params: { period } }),
  refresh: (productId: number) => api.post(`/api/products/${productId}/refresh`),
};

// ---- Tracking (Part I & J REST Contract) ----
export const trackingApi = {
  list: (params?: { skip?: number; limit?: number }) =>
    api.get('/api/tracking', { params }),
  create: (data: { product_url: string; target_min_price?: number; target_max_price?: number }) =>
    api.post('/api/tracking', data),
  get: (id: number) => api.get(`/api/tracking/${id}`),
  update: (id: number, data: object) => api.patch(`/api/tracking/${id}`, data),
  delete: (id: number) => api.delete(`/api/tracking/${id}`),
};

// ---- Alerts ----
export const alertsApi = {
  create: (data: object) => api.post('/api/alerts', data),
  list: () => api.get('/api/alerts'),
  update: (id: number, data: object) => api.put(`/api/alerts/${id}`, data),
  delete: (id: number) => api.delete(`/api/alerts/${id}`),
};

// ---- Notifications ----
export const notificationsApi = {
  list: (unread_only?: boolean) => api.get('/api/notifications', { params: { unread_only } }),
  unreadCount: () => api.get('/api/notifications/unread-count'),
  markRead: (id: number) => api.post(`/api/notifications/${id}/read`),
  markAllRead: () => api.post('/api/notifications/read-all'),
};

// ---- Dashboard ----
export const dashboardApi = {
  stats: () => api.get('/api/admin/dashboard-stats'),
};

// ---- Admin ----
export const adminApi = {
  stats: () => api.get('/api/admin/stats'),
  users: () => api.get('/api/admin/users'),
};

// ---- Trending Deals ----
export const dealsApi = {
  getTrending: (params?: { store?: string; category?: string }) =>
    api.get('/api/trending-deals', { params }),
  refresh: () =>
    api.post('/api/trending-deals/refresh'),
};

export default api;
