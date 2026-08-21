import api from './api';
import { ChefListResponse } from '@/types/chef';

export async function fetchChefs(
  cuisine?: string,
  locality?: string,
): Promise<ChefListResponse> {
  const params: Record<string, string> = {};
  if (cuisine) params.cuisine = cuisine;
  if (locality) params.locality = locality;
  const { data } = await api.get<ChefListResponse>('/api/chefs', { params });
  return data;
}
