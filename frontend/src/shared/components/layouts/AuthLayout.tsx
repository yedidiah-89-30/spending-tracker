'use client';

import React from 'react';
import { ThemeToggle } from '@/shared/components/navigation/ThemeToggle';
import { cn } from '@/shared/lib/utils/format';

interface AuthLayoutProps {
  children: React.ReactNode;
  title?: string;
  subtitle?: string;
  className?: string;
}

export function AuthLayout({ children, title, subtitle, className }: AuthLayoutProps) {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-background via-background to-muted/20 p-4">
      <div className="absolute top-4 right-4">
        <ThemeToggle />
      </div>

      <div className={cn('w-full max-w-md space-y-6', className)}>
        {(title || subtitle) && (
          <div className="text-center space-y-2">
            {title && (
              <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text text-transparent">
                {title}
              </h1>
            )}
            {subtitle && (
              <p className="text-sm text-muted-foreground">{subtitle}</p>
            )}
          </div>
        )}

        {children}
      </div>

      <div className="absolute bottom-4 left-4 text-xs text-muted-foreground">
        © {new Date().getFullYear()} Finance Tracker
      </div>
    </div>
  );
}