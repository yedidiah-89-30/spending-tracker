import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { authService } from '../services/auth.service';
import { useToast } from '@/shared/hooks/useToast';
import { getErrorMessage } from '@/shared/lib/api/error';
import type { LoginRequest } from '../types';
import type { RegisterFormData } from '../validations/auth.schema';

export const AUTH_QUERY_KEY = 'auth';

export function useAuth() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const { data: user, isLoading: isLoadingUser, refetch } = useQuery({
    queryKey: [AUTH_QUERY_KEY, 'user'],
    queryFn: authService.getCurrentUser,
    enabled: authService.isAuthenticated(),
    retry: false,
    staleTime: 5 * 60 * 1000,
  });

  const loginMutation = useMutation({
    mutationFn: (data: LoginRequest) => authService.login(data),

    onSuccess: (data) => {
      queryClient.setQueryData([AUTH_QUERY_KEY, 'user'], data.user);
      setIsAuthenticated(true);

      toast({
        title: 'Welcome back!',
        description: `Hello, ${data.user.full_name}`,
      });

      router.push('/dashboard');
    },

    onError: (error: any) => {
      toast({
        title: 'Login failed',
        description: getErrorMessage(error),
        variant: 'destructive',
      });
    },
  });

  const registerMutation = useMutation({
    mutationFn: (data: RegisterFormData) =>
      authService.register({
        full_name: data.name,
        email: data.email,
        password: data.password,
      }),

    onSuccess: (data) => {
      queryClient.setQueryData([AUTH_QUERY_KEY, 'user'], data.user);
      setIsAuthenticated(true);

      toast({
        title: 'Account created!',
        description: 'Welcome to Finance Tracker',
      });

      router.push('/dashboard');
    },

    onError: (error: any) => {
      toast({
        title: 'Registration failed',
        description: getErrorMessage(error),
        variant: 'destructive',
      });
    },
  });

  const logoutMutation = useMutation({
    mutationFn: authService.logout,

    onSuccess: () => {
      queryClient.clear();
      setIsAuthenticated(false);

      toast({
        title: 'Logged out',
        description: 'You have been successfully logged out',
      });

      router.push('/login');
    },

    onError: (error: any) => {
      toast({
        title: 'Logout failed',
        description: getErrorMessage(error),
        variant: 'destructive',
      });
    },
  });

  useEffect(() => {
    setIsAuthenticated(authService.isAuthenticated());
  }, []);

  return {
    user,
    isLoading: isLoadingUser,
    isAuthenticated,

    login: loginMutation.mutateAsync,
    isLoggingIn: loginMutation.isPending,

    register: registerMutation.mutateAsync,
    isRegistering: registerMutation.isPending,

    logout: logoutMutation.mutateAsync,
    isLoggingOut: logoutMutation.isPending,

    refetchUser: refetch,
  };
}