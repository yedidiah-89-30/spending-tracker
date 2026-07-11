import { DashboardLayout } from '@/shared/components/layouts/DashboardLayout';

export default function DashboardLayoutPage({
  children,
}: {
  children: React.ReactNode;
}) {
  return <DashboardLayout>{children}</DashboardLayout>;
}
