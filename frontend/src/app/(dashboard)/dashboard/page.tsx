'use client';

import { DashboardStats } from '@/features/dashboard/components/DashboardStats';
import { IncomeChart } from '@/features/dashboard/components/IncomeChart';
import { RecentTransactions } from '@/features/dashboard/components/RecentTransactions';
import { QuickActions } from '@/features/dashboard/components/QuickActions';

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome back! Here's an overview of your finances.
        </p>
      </div>

      <DashboardStats />

      <div className="grid gap-6 lg:grid-cols-7">
        <div className="lg:col-span-4">
          <IncomeChart />
        </div>
        <div className="lg:col-span-3">
          <QuickActions />
        </div>
      </div>

      <RecentTransactions />
    </div>
  );
}
