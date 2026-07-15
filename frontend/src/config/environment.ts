export const env = {
  apiBaseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api/v1',
  apiTimeout: parseInt(process.env.NEXT_PUBLIC_API_TIMEOUT || '30000', 10),
  enableAnalytics: process.env.NEXT_PUBLIC_ENABLE_ANALYTICS === 'true',
  appName: process.env.NEXT_PUBLIC_APP_NAME || 'Finance Tracker',
  appUrl: process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000',
  isDevelopment: process.env.NODE_ENV === 'development',
  isProduction: process.env.NODE_ENV === 'production',
  isTest: process.env.NODE_ENV === 'test',
} as const;

const requiredEnvVars = ['NEXT_PUBLIC_API_URL'] as const;
const missingEnvVars = requiredEnvVars.filter(
  (key) => !process.env[key]
);

if (missingEnvVars.length > 0 && process.env.NODE_ENV === 'production') {
  throw new Error(
    `Missing required environment variables: ${missingEnvVars.join(', ')}`
  );
}
