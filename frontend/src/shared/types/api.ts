export interface APIResponse<T = any> {
  data: T;
  status: number;
  message: string;
  timestamp?: string;
}

export interface APIErrorResponse {
  status: number;
  message: string;
  code: string;
  details?: any;
  timestamp?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  totalPages: number;
  limit: number;
  hasNext: boolean;
  hasPrev: boolean;
}

export interface PaginationParams {
  page?: number;
  limit?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface FilterParams {
  search?: string;
  startDate?: string;
  endDate?: string;
  [key: string]: any;
}