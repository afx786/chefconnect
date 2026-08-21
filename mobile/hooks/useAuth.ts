import { useState, useCallback } from 'react';
import { AuthState, AUTH_INITIAL_STATE } from '@/context/AuthContext';
import { login as apiLogin, signup as apiSignup } from '@/services/authService';
import { LoginRequest, SignupRequest } from '@/types/auth';

export function useAuth() {
  const [state, setState] = useState<AuthState>(AUTH_INITIAL_STATE);

  const login = useCallback(async (data: LoginRequest) => {
    setState((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const result = await apiLogin(data);
      setState({ user: result.user, loading: false, error: null });
    } catch (e: any) {
      setState((prev) => ({
        ...prev,
        loading: false,
        error: e?.response?.data?.detail || e?.message || 'Login failed',
      }));
    }
  }, []);

  const signup = useCallback(async (data: SignupRequest) => {
    setState((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const result = await apiSignup(data);
      setState({ user: result.user, loading: false, error: null });
    } catch (e: any) {
      setState((prev) => ({
        ...prev,
        loading: false,
        error: e?.response?.data?.detail || e?.message || 'Signup failed',
      }));
    }
  }, []);

  const logout = useCallback(() => {
    setState(AUTH_INITIAL_STATE);
  }, []);

  const clearError = useCallback(() => {
    setState((prev) => ({ ...prev, error: null }));
  }, []);

  return { ...state, login, signup, logout, clearError };
}
