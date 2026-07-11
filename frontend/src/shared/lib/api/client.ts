import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import { env } from '@/config/environment';
import { setupInterceptors } from './interceptors';

let axiosInstance: AxiosInstance | null = null;

export const getApiClient = (): AxiosInstance => {
  if (!axiosInstance) {
    axiosInstance = axios.create({
      baseURL: env.apiBaseUrl,
      timeout: env.apiTimeout,
      headers: {
        'Content-Type': 'application/json',
      },
    });
    setupInterceptors(axiosInstance);
  }
  return axiosInstance;
};

export const apiClient = getApiClient();

export const apiRequest = async <T>(
  config: AxiosRequestConfig
): Promise<T> => {
  try {
    const response = await apiClient.request<T>(config);
    return response.data;
  } catch (error) {
    throw error;
  }
};