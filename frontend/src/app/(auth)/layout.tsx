import { AuthLayout } from '@/shared/components/layouts/AuthLayout';

export default function AuthLayoutPage({
  children,
}: {
  children: React.ReactNode;
}) {
  return <AuthLayout>{children}</AuthLayout>;
}
