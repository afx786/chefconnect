import { useState, useEffect, useCallback } from 'react';
import { Chef } from '@/types/chef';
import { fetchChefs } from '@/services/chefService';

export function useChefs() {
  const [chefs, setChefs] = useState<Chef[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [cuisine, setCuisine] = useState<string | undefined>();
  const [locality, setLocality] = useState<string | undefined>();

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchChefs(cuisine, locality);
      setChefs(data.chefs);
    } catch (e: any) {
      setError(e?.message || 'Failed to load chefs');
    } finally {
      setLoading(false);
    }
  }, [cuisine, locality]);

  useEffect(() => {
    load();
  }, [load]);

  return {
    chefs,
    loading,
    error,
    cuisine,
    locality,
    setCuisine,
    setLocality,
    refetch: load,
  };
}
