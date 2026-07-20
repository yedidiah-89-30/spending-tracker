import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { incomeService } from '../services/income.service';
import { useToast } from '@/shared/hooks/useToast';
import { getErrorMessage } from '@/shared/lib/api/error';
import { DASHBOARD_QUERY_KEY } from '@/features/dashboard/hooks/useDashboard';
import type { IncomeCreate, IncomeUpdate, IncomeFilters } from '../types';

const INCOME_QUERY_KEY = 'income';

export function useIncome(filters?: IncomeFilters) {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const query = useQuery({
    queryKey: [INCOME_QUERY_KEY, filters],
    queryFn: () => incomeService.getAll(filters),
    staleTime: 2 * 60 * 1000,
  });

  const createMutation = useMutation({
    mutationFn: (data: IncomeCreate) => incomeService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [INCOME_QUERY_KEY] });
      queryClient.invalidateQueries({ queryKey: [DASHBOARD_QUERY_KEY] });
      toast({
        title: 'Income added',
        description: 'Your income has been added successfully',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Failed to add income',
        description: getErrorMessage(error),
        variant: 'destructive',
      });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: IncomeUpdate }) =>
      incomeService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [INCOME_QUERY_KEY] });
      queryClient.invalidateQueries({ queryKey: [DASHBOARD_QUERY_KEY] });
      toast({
        title: 'Income updated',
        description: 'Your income has been updated successfully',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Failed to update income',
        description: getErrorMessage(error),
        variant: 'destructive',
      });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => incomeService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [INCOME_QUERY_KEY] });
      queryClient.invalidateQueries({ queryKey: [DASHBOARD_QUERY_KEY] });
      toast({
        title: 'Income deleted',
        description: 'Your income has been deleted successfully',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Failed to delete income',
        description: getErrorMessage(error),
        variant: 'destructive',
      });
    },
  });

  return {
    data: query.data?.items || [],
    total: query.data?.total || 0,
    totalPages: query.data?.totalPages || 0,
    isLoading: query.isLoading,
    error: query.error,
    refetch: query.refetch,
    createIncome: createMutation.mutateAsync,
    isCreating: createMutation.isPending,
    updateIncome: updateMutation.mutateAsync,
    isUpdating: updateMutation.isPending,
    deleteIncome: deleteMutation.mutateAsync,
    isDeleting: deleteMutation.isPending,
  };
}