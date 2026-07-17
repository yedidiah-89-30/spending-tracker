export interface Income {
  id: string;
  userId: string;
  amount: number;
  source: string;
  category: string;
  date: string;
  description?: string;
  recurring: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface IncomeCreate {
  amount: number;
  source: string;
  category: string;
  date: string;
  description?: string;
  recurring: boolean;
}

export interface IncomeUpdate {
  amount?: number;
  source?: string;
  category?: string;
  date?: string;
  description?: string;
  recurring?: boolean;
}

export interface IncomeFilters {
  search?: string;
  category?: string;
  startDate?: string;
  endDate?: string;
  minAmount?: number;
  maxAmount?: number;
  recurring?: boolean;
  sortBy?: 'date' | 'amount' | 'source';
  sortOrder?: 'asc' | 'desc';
  page?: number;
  limit?: number;
}

export interface IncomeListResponse {
  items: Income[];
  total: number;
  page: number;
  totalPages: number;
  limit: number;
  hasNext: boolean;
  hasPrev: boolean;
}

export const INCOME_CATEGORIES = [
  { label: 'Salary', value: 'salary' },
  { label: 'Business', value: 'business' },
  { label: 'Freelance', value: 'freelance' },
  { label: 'Investment', value: 'investment' },
  { label: 'Rental', value: 'rental' },
  { label: 'Dividend', value: 'dividend' },
  { label: 'Interest', value: 'interest' },
  { label: 'Gift', value: 'gift' },
  { label: 'Other', value: 'other' },
] as const;

export type IncomeCategory = typeof INCOME_CATEGORIES[number]['value'];