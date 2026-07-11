'use client';

import { IncomeList } from '@/features/income/components/IncomeList';
import { IncomeStats } from '@/features/income/components/IncomeStats';

export default function IncomePage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Income</h1>
        <p className="text-muted-foreground">
          Manage and track all your income sources.
        </p>
      </div>

      <IncomeStats />
      <IncomeList />
    </div>
  );
}
