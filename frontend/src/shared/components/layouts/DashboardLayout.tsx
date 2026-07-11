'use client';

import React, { useState, useEffect } from 'react';
import { Sidebar } from '@/shared/components/navigation/Sidebar';
import { Header } from '@/shared/components/navigation/Header';
import { ErrorBoundary } from '@/shared/components/feedback/ErrorBoundary';
import { cn } from '@/shared/lib/utils/format';
import { useMediaQuery } from '@/shared/hooks/useMediaQuery';

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const isMobile = useMediaQuery('(max-width: 1024px)');

  // Auto-close sidebar on mobile
  useEffect(() => {
    if (isMobile) {
      setSidebarOpen(false);
    } else {
      setSidebarOpen(true);
    }
  }, [isMobile]);

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      <Sidebar open={sidebarOpen} onToggle={toggleSidebar} />

      <div
        className={cn(
          'flex-1 flex flex-col overflow-hidden transition-all duration-300',
          sidebarOpen && !isMobile ? 'lg:ml-64' : 'ml-0'
        )}
      >
        <Header onMenuClick={toggleSidebar} />

        <main className="flex-1 overflow-y-auto p-4 md:p-6 bg-muted/5">
          <ErrorBoundary>
            <div className="max-w-7xl mx-auto">
              {children}
            </div>
          </ErrorBoundary>
        </main>
      </div>
    </div>
  );
}