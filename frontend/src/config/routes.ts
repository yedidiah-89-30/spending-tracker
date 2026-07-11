export const ROUTES = {
  auth: {
    login: '/login',
    register: '/register',
    forgotPassword: '/forgot-password',
    resetPassword: '/reset-password',
  },
  dashboard: {
    home: '/dashboard',
    income: '/income',
    expenses: '/expenses',
    budgets: '/budgets',
    savings: '/savings',
    subscriptions: '/subscriptions',
    reports: '/reports',
    settings: '/settings',
  },
} as const;

export type AuthRoute = typeof ROUTES.auth[keyof typeof ROUTES.auth];
export type DashboardRoute = typeof ROUTES.dashboard[keyof typeof ROUTES.dashboard];
