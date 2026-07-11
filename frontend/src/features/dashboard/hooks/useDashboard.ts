import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/shared/lib/api/client';
import { handleAPIError } from '@/shared/lib/api/error';
import type { DashboardData } from '../types';

const DASHBOARD_QUERY_KEY = 'dashboard';

export function useDashboard() {
  return useQuery({
    queryKey: [DASHBOARD_QUERY_KEY],
    queryFn: async (): Promise<DashboardData> => {
      try {
        const response = await apiClient.get<DashboardData>('/dashboard');
        return response.data;
      } catch (error) {
        throw handleAPIError(error);
      }
    },
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: true,
  });
}
