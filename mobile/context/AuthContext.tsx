import { User } from '@/types/auth';

export interface AuthState {
  user: User | null;
  loading: boolean;
  error: string | null;
}

export interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  signup: (name: string, email: string, phone: string, password: string) => Promise<void>;
  logout: () => void;
  clearError: () => void;
}

export const AUTH_INITIAL_STATE: AuthState = {
  user: null,
  loading: false,
  error: null,
};
