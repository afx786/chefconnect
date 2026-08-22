import api from './api';
import { LoginRequest, SignupRequest, TokenResponse, SignupResponse } from '@/types/auth';
import { setToken } from './tokenStorage';

export async function login(data: LoginRequest): Promise<TokenResponse> {
  const response = await api.post<TokenResponse>('/api/auth/login', data);
  await setToken(response.data.access_token);
  return response.data;
}

export async function signup(data: SignupRequest): Promise<SignupResponse> {
  const response = await api.post<SignupResponse>('/api/auth/signup', data);
  return response.data;
}
