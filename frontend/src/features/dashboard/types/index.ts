export interface DashboardStats {
  totalIncome: number;
  totalExpenses: number;
  balance: number;
  savings: number;
  incomeChange: number;
  expensesChange: number;
  balanceChange: number;
  savingsChange: number;
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
  recentTransactions: Transaction[];
  incomeData: { month: string; amount: number }[];
}
