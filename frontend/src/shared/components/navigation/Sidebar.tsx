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
  ChevronLeft,
  ChevronRight,
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

interface SidebarProps {
  open: boolean;
  onToggle: () => void;
}

export function Sidebar({ open, onToggle }: SidebarProps) {
  const pathname = usePathname();
  const { logout, isLoggingOut } = useAuth();

  return (
    <>
      {/* Mobile overlay */}
      {open && (
        <div
          className="fixed inset-0 z-40 bg-background/80 backdrop-blur-sm lg:hidden"
          onClick={onToggle}
          aria-hidden="true"
        />
      )}

      <aside
        className={cn(
          'fixed left-0 top-0 z-40 h-screen bg-card border-r border-border transition-transform duration-300',
          'w-64',
          !open && '-translate-x-full lg:translate-x-0 lg:w-20'
        )}
        role="navigation"
        aria-label="Main navigation"
      >
        {/* Logo */}
        <div className="flex h-16 items-center justify-between border-b border-border px-4">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-primary flex items-center justify-center">
              <span className="text-primary-foreground font-bold text-sm">FD</span>
            </div>
            <span
              className={cn(
                'text-lg font-bold transition-opacity duration-300',
                !open && 'lg:opacity-0 lg:w-0'
              )}
            >
              Finance
            </span>
          </div>
          <Button
            variant="ghost"
            size="icon"
            className="hidden lg:flex h-8 w-8"
            onClick={onToggle}
            aria-label={open ? 'Collapse sidebar' : 'Expand sidebar'}
          >
            {open ? <ChevronLeft className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
          </Button>
        </div>

        {/* Navigation */}
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
                  'flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-all duration-200',
                  isActive
                    ? 'bg-primary text-primary-foreground shadow-sm'
                    : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground',
                  !open && 'lg:justify-center lg:px-2'
                )}
                title={!open ? item.name : undefined}
              >
                <Icon className="h-5 w-5 flex-shrink-0" aria-hidden="true" />
                <span
                  className={cn(
                    'transition-opacity duration-300',
                    !open && 'lg:opacity-0 lg:w-0 lg:overflow-hidden'
                  )}
                >
                  {item.name}
                </span>
              </Link>
            );
          })}
        </nav>

        {/* Logout */}
        <div className="border-t border-border p-4">
          <Button
            variant="ghost"
            className={cn(
              'w-full justify-start gap-3 text-muted-foreground hover:text-destructive hover:bg-destructive/10',
              !open && 'lg:justify-center lg:px-2'
            )}
            onClick={() => logout()}
            disabled={isLoggingOut}
            aria-label="Logout"
          >
            <LogOut className="h-5 w-5 flex-shrink-0" aria-hidden="true" />
            <span
              className={cn(
                'transition-opacity duration-300',
                !open && 'lg:opacity-0 lg:w-0 lg:overflow-hidden'
              )}
            >
              {isLoggingOut ? 'Logging out...' : 'Logout'}
            </span>
          </Button>
        </div>
      </aside>
    </>
  );
}