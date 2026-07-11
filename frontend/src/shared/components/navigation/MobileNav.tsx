'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/shared/lib/utils/format';
import { ROUTES } from '@/config/routes';
import {
  LayoutDashboard,
  DollarSign,
  TrendingDown,
  TrendingUp,
  PiggyBank,
  CreditCard,
  BarChart3,
  Settings,
  LogOut,
  X,
} from 'lucide-react';
import { Button } from '@/shared/components/ui/Button';
import { useAuth } from '@/features/auth/hooks/useAuth';

const navigationItems = [
  { name: 'Dashboard', href: ROUTES.dashboard.home, icon: LayoutDashboard },
  { name: 'Income', href: ROUTES.dashboard.income, icon: DollarSign },
  { name: 'Expenses', href: ROUTES.dashboard.expenses, icon: TrendingDown },
  { name: 'Budgets', href: ROUTES.dashboard.budgets, icon: TrendingUp },
  { name: 'Savings', href: ROUTES.dashboard.savings, icon: PiggyBank },
  { name: 'Subscriptions', href: ROUTES.dashboard.subscriptions, icon: CreditCard },
  { name: 'Reports', href: ROUTES.dashboard.reports, icon: BarChart3 },
  { name: 'Settings', href: ROUTES.dashboard.settings, icon: Settings },
];

interface MobileNavProps {
  open: boolean;
  onClose: () => void;
}

export function MobileNav({ open, onClose }: MobileNavProps) {
  const pathname = usePathname();
  const { logout, isLoggingOut } = useAuth();

  if (!open) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Mobile menu */}
      <div className="fixed inset-y-0 right-0 z-50 w-full max-w-xs bg-card shadow-lg">
        <div className="flex h-16 items-center justify-between border-b border-border px-4">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-primary flex items-center justify-center">
              <span className="text-primary-foreground font-bold text-sm">FD</span>
            </div>
            <span className="text-lg font-bold">Finance</span>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            aria-label="Close menu"
          >
            <X className="h-5 w-5" />
          </Button>
        </div>

        <nav className="flex-1 overflow-y-auto p-4 space-y-1" role="menubar">
          {navigationItems.map((item) => {
            const isActive = pathname === item.href || pathname?.startsWith(`${item.href}/`);
            const Icon = item.icon;

            return (
              <Link
                key={item.name}
                href={item.href}
                role="menuitem"
                aria-current={isActive ? 'page' : undefined}
                className={cn(
                  'flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors',
                  isActive
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                )}
                onClick={onClose}
              >
                <Icon className="h-5 w-5 flex-shrink-0" aria-hidden="true" />
                {item.name}
              </Link>
            );
          })}

          <div className="border-t border-border my-4 pt-4">
            <Button
              variant="ghost"
              className="w-full justify-start gap-3 text-muted-foreground hover:text-destructive hover:bg-destructive/10"
              onClick={() => {
                logout();
                onClose();
              }}
              disabled={isLoggingOut}
            >
              <LogOut className="h-5 w-5 flex-shrink-0" aria-hidden="true" />
              {isLoggingOut ? 'Logging out...' : 'Logout'}
            </Button>
          </div>
        </nav>
      </div>
    </>
  );
}