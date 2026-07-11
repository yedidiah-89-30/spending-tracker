import { apiClient } from '@/shared/lib/api/client';
import { handleAPIError } from '@/shared/lib/api/error';
import type { Income, IncomeCreate, IncomeUpdate, IncomeFilters, IncomeListResponse } from '../types';

export const incomeService = {
  async getAll(filters?: IncomeFilters): Promise<IncomeListResponse> {
    try {
      const response = await apiClient.get<IncomeListResponse>('/income', { params: filters });
      return response.data;
    } catch (error) {
      throw handleAPIError(error);
    }
  },

  async getById(id: string): Promise<Income> {
    try {
      const response = await apiClient.get<Income>(/income/);
      return response.data;
    } catch (error) {
      throw handleAPIError(error);
    }
  },

  async create(data: IncomeCreate): Promise<Income> {
    try {
      const response = await apiClient.post<Income>('/income', data);
      return response.data;
    } catch (error) {
      throw handleAPIError(error);
    }
  },

  async update(id: string, data: IncomeUpdate): Promise<Income> {
    try {
      const response = await apiClient.put<Income>(/income/, data);
      return response.data;
    } catch (error) {
      throw handleAPIError(error);
    }
  },

  async delete(id: string): Promise<void> {
    try {
      await apiClient.delete(/income/);
    } catch (error) {
      throw handleAPIError(error);
    }
  },

  async getStats(): Promise<{ total: number; average: number; count: number; categories: Record<string, number> }> {
    try {
      const response = await apiClient.get<{ total: number; average: number; count: number; categories: Record<string, number> }>(
        '/income/stats'
      );
      return response.data;
    } catch (error) {
      throw handleAPIError(error);
    }
  },
};
