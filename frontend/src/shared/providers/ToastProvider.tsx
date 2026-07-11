'use client';

import { Toaster } from '@/shared/components/ui/Toaster';

export function ToastProvider({ children }: { children: React.ReactNode }) {
  return (
    <>
      {children}
      <Toaster />
    </>
  );
}