'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/components/ui/Card';
import { Button } from '@/shared/components/ui/Button';
import { Plus, FileText, Download, Settings } from 'lucide-react';
import Link from 'next/link';
import { ROUTES } from '@/config/routes';

export function QuickActions() {
  return (
    <Card className="border-border/50">
      <CardHeader>
        <CardTitle>Quick Actions</CardTitle>
        <CardDescription>Common tasks and shortcuts</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        <Link href={ROUTES.dashboard.income} className="block">
          <Button className="w-full justify-start" variant="outline">
            <Plus className="h-4 w-4 mr-2" />
            Add Income
          </Button>
        </Link>
        <Link href={ROUTES.dashboard.expenses} className="block">
          <Button className="w-full justify-start" variant="outline">
            <Plus className="h-4 w-4 mr-2" />
            Add Expense
          </Button>
        </Link>
        <Button className="w-full justify-start" variant="outline">
          <FileText className="h-4 w-4 mr-2" />
          Generate Report
        </Button>
        <Button className="w-full justify-start" variant="outline">
          <Download className="h-4 w-4 mr-2" />
          Export Data
        </Button>
        <Link href={ROUTES.dashboard.settings} className="block">
          <Button className="w-full justify-start" variant="outline">
            <Settings className="h-4 w-4 mr-2" />
            Settings
          </Button>
        </Link>
      </CardContent>
    </Card>
  );
}
