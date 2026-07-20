'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/shared/components/ui/Card';
import { Skeleton } from '@/shared/components/ui/Skeleton';
import { cn } from '@/shared/lib/utils/format';
import { useDashboard } from '../hooks/useDashboard';
import { TrendingUp, TrendingDown, Wallet, PiggyBank } from 'lucide-react';
import { formatCurrency } from '@/shared/lib/utils/format';

interface StatCardProps {
  title: string;
  value: string;
  icon: React.ReactNode;
  change?: number;
  variant?: 'default' | 'success' | 'destructive';
}

function StatCard({ title, value, icon, change, variant = 'default' }: StatCardProps) {
  const isPositive = change && change > 0;
  const isNegative = change && change < 0;

  return (
    <Card className="border-border/50">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
        <div className="h-4 w-4 text-muted-foreground">{icon}</div>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {change !== undefined && (
          <div className="flex items-center gap-1 text-xs mt-1">
            <span
              className={cn(
                'flex items-center font-medium',
                isPositive && 'text-emerald-600 dark:text-emerald-400',
                isNegative && 'text-red-600 dark:text-red-400',
                !isPositive && !isNegative && 'text-muted-foreground'
              )}
            >
              {isPositive && <TrendingUp className="h-3 w-3 mr-0.5" />}
              {isNegative && <TrendingDown className="h-3 w-3 mr-0.5" />}
              {isPositive ? '+' : ''}{change}%
            </span>
            <span className="text-muted-foreground">from last month</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export function DashboardStats() {
  const { data, isLoading, error } = useDashboard();

  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Card key={i} className="border-border/50">
            <CardHeader className="pb-2">
              <Skeleton className="h-4 w-24" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-8 w-32" />
              <Skeleton className="h-4 w-40 mt-2" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg border border-destructive/20 bg-destructive/10 p-4 text-center text-sm text-destructive">
        Failed to load dashboard statistics
      </div>
    );
  }

  const stats = data!;

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <StatCard
        title="Total Income"
        value={formatCurrency(stats.total_income)}
        icon={<TrendingUp className="h-4 w-4" />}
        change={stats.income_change}
      />
      <StatCard
        title="Total Expenses"
        value={formatCurrency(stats.total_expenses)}
        icon={<TrendingDown className="h-4 w-4" />}
        change={stats.expenses_change}
        variant="destructive"
      />
      <StatCard
        title="Net Profit/Loss"
        value={formatCurrency(stats.net_profit_loss)}
        icon={<Wallet className="h-4 w-4" />}
        change={stats.net_profit_loss_change}
        variant={stats.net_profit_loss >= 0 ? 'success' : 'destructive'}
      />
      <StatCard
  title="Savings"
  value={formatCurrency(stats.total_savings)}
  icon={<PiggyBank className="h-4 w-4" />}
/>
    </div>
  );
}