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
        const response = await apiClient.get('/dashboard/summary');

        const data = response.data;

        return {
          stats: {
            totalIncome: Number(data.total_income),
            totalExpenses: Number(data.total_expenses),
            balance: Number(data.net_profit_loss),
            savings: Number(data.total_savings),

            // Backend doesn't provide these yet.
            incomeChange: 0,
            expensesChange: 0,
            balanceChange: 0,
            savingsChange: 0,
          },

          recentTransactions: data.recent_transactions.map((t: any) => ({
            id: String(t.id),
            type: t.type,
            amount: Number(t.amount),
            description: t.description,
            category: t.category,
            date: t.date,
            status: 'completed',
          })),

          // Backend hasn't implemented chart data yet.
          incomeData: [],
        };
      } catch (error) {
        throw handleAPIError(error);
      }
    },
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: true,
  });
}