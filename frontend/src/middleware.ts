import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { ROUTES } from '@/config/routes';

const PUBLIC_PATHS = [
  ROUTES.auth.login,
  ROUTES.auth.register,
  ROUTES.auth.forgotPassword,
  ROUTES.auth.resetPassword,
];

const PROTECTED_PATHS = [
  ROUTES.dashboard.home,
  ROUTES.dashboard.income,
  ROUTES.dashboard.expenses,
  ROUTES.dashboard.budgets,
  ROUTES.dashboard.savings,
  ROUTES.dashboard.subscriptions,
  ROUTES.dashboard.reports,
  ROUTES.dashboard.settings,
];

export function middleware(request: NextRequest) {
  const token = request.cookies.get('auth_token')?.value;
  const { pathname } = request.nextUrl;

  const isPublicPath = PUBLIC_PATHS.some(path => pathname.startsWith(path));
  const isProtectedPath = PROTECTED_PATHS.some(path => pathname.startsWith(path));
  const isAuthPath = PUBLIC_PATHS.some(path => pathname === path);

  if (token && isAuthPath) {
    return NextResponse.redirect(new URL(ROUTES.dashboard.home, request.url));
  }

  if (!token && isProtectedPath) {
    const loginUrl = new URL(ROUTES.auth.login, request.url);
    loginUrl.searchParams.set('redirect', pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico|public|api).*)',
  ],
};
