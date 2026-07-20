import { apiClient } from './client';
import { handleAPIError } from './error';
import type { DashboardData } from '@/features/dashboard/types';

export const dashboardAPI = {
  async getStats(): Promise<DashboardData> {
    try {
      const response = await apiClient.get('/dashboard/summary');

      console.log("Dashboard API Response:", response.data);

      return response.data;
    } catch (error) {
      throw handleAPIError(error);
    }
  },
};