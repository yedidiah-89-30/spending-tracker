import { apiClient } from '@/shared/lib/api/client';
import { handleAPIError } from '@/shared/lib/api/error';
import type {
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  RegisterResponse,
  ForgotPasswordRequest,
  ResetPasswordRequest,
  User,
} from '../types';

const TOKEN_KEY = 'auth_token';
const REFRESH_TOKEN_KEY = 'refresh_token';

export const authService = {
  async login(data: LoginRequest): Promise<LoginResponse> {
    try {
      const response = await apiClient.post<LoginResponse>('/auth/login', data);
      this.setTokens(
        response.data.access_token,
        response.data.refresh_token
      );
      return response.data;
    } catch (error) {
      throw handleAPIError(error);
    }
  },

  async register(data: RegisterRequest): Promise<RegisterResponse> {
    try {
      const response = await apiClient.post<RegisterResponse>('/auth/register', data);
      this.setTokens(
        response.data.access_token,
        response.data.refresh_token
      );
      return response.data;
    } catch (error) {
      throw handleAPIError(error);
    }
  },

  async forgotPassword(data: ForgotPasswordRequest): Promise<void> {
    try {
      await apiClient.post('/auth/forgot-password', data);
    } catch (error) {
      throw handleAPIError(error);
    }
  },

  async resetPassword(data: ResetPasswordRequest): Promise<void> {
    try {
      await apiClient.post('/auth/reset-password', data);
    } catch (error) {
      throw handleAPIError(error);
    }
  },

  async refreshToken(refreshToken: string): Promise<{ token: string; refreshToken: string }> {
    try {
      const response = await apiClient.post<{ token: string; refreshToken: string }>(
        '/auth/refresh',
        { refreshToken }
      );
      return response.data;
    } catch (error) {
      throw handleAPIError(error);
    }
  },

  async logout(): Promise<void> {
    try {
      await apiClient.post('/auth/logout');
    } finally {
      this.clearTokens();
    }
  },

  async getCurrentUser(): Promise<User> {
    try {
      const response = await apiClient.get<User>('/auth/me');
      return response.data;
    } catch (error) {
      throw handleAPIError(error);
    }
  },

  setTokens(token: string, refreshToken: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem(TOKEN_KEY, token);
      localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
      document.cookie = `auth_token=${token}; path=/; max-age=86400; SameSite=Lax`;
    }
  },

  getToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem(TOKEN_KEY);
    }
    return null;
  },

  getRefreshToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem(REFRESH_TOKEN_KEY);
    }
    return null;
  },

  clearTokens(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(REFRESH_TOKEN_KEY);
      document.cookie = 'auth_token=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;';
    }
  },

  isAuthenticated(): boolean {
    return !!this.getToken();
  },
};