import { useQuery, useQueryClient } from '@tanstack/react-query';
import { dashboardAPI } from '@/shared/lib/api/dashboard';
import type { DashboardData } from '../types';

export const DASHBOARD_QUERY_KEY = 'dashboard';

export function useDashboard() {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: [DASHBOARD_QUERY_KEY],
    queryFn: async (): Promise<DashboardData> => {
      const data = await dashboardAPI.getStats();
      return data;
    },
    staleTime: 2 * 60 * 1000,
    refetchOnWindowFocus: true,
  });

  // Function to invalidate dashboard cache
  const invalidateDashboard = () => {
    queryClient.invalidateQueries({ queryKey: [DASHBOARD_QUERY_KEY] });
  };

  return {
    data: query.data,
    isLoading: query.isLoading,
    error: query.error,
    refetch: query.refetch,
    invalidateDashboard,
  };
}