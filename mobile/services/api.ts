import axios from 'axios';
import { API_BASE_URL } from '@/constants/config';
import { getToken, removeToken } from './tokenStorage';

const AUTH_PATH_PREFIX = '/api/auth/';

let onSessionExpired: (() => void) | null = null;

export function setOnSessionExpired(handler: (() => void) | null): void {
  onSessionExpired = handler;
}

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
});

api.interceptors.request.use(async (config) => {
  const token = await getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const requestUrl: string = error.config?.url ?? '';
    const isAuthRequest = requestUrl.startsWith(AUTH_PATH_PREFIX);
    if (error.response?.status === 401 && !isAuthRequest) {
      await removeToken();
      if (onSessionExpired) {
        onSessionExpired();
      }
    }
    return Promise.reject(error);
  },
);

export default api;
