export interface DashboardStats {
  total_income: number;
  total_expenses: number;
  net_profit_loss: number;
  balance: number;
  income_change: number;
  expenses_change: number;
  net_profit_loss_change: number;
  balance_change: number;
}

export interface Transaction {
  id: string;
  type: 'income' | 'expense';
  amount: number;
  description: string;
  category: string;
  date: string;
  status: 'completed' | 'pending' | 'failed';
}

export interface DashboardData {
  stats: DashboardStats;
  recent_transactions: Transaction[];
  income_data: { month: string; amount: number }[];
}