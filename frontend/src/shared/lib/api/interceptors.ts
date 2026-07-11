import { AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import { authService } from '@/features/auth/services/auth.service';
import { APIError, handleAPIError } from './error';

export const setupInterceptors = (client: AxiosInstance) => {
  // Request interceptor
  client.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
      const token = authService.getToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  // Response interceptor
  client.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config;

      // Handle 401 - Token expired
      if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;
        try {
          const refreshToken = authService.getRefreshToken();
          if (refreshToken) {
            const response = await authService.refreshToken(refreshToken);
            authService.setTokens(response.token, response.refreshToken);
            originalRequest.headers.Authorization = `Bearer ${response.token}`;
            return client(originalRequest);
          }
        } catch {
          authService.clearTokens();
          if (typeof window !== 'undefined') {
            window.location.href = '/login';
          }
          return Promise.reject(error);
        }
      }

      return Promise.reject(handleAPIError(error));
    }
  );
};