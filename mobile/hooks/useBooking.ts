import { useState, useCallback } from 'react';
import { Booking, BookingCreate } from '@/types/booking';
import { createBooking } from '@/services/bookingService';
import { normalizeApiError } from '@/utils/apiErrors';

export function useBooking() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<Booking | null>(null);

  const submit = useCallback(async (payload: BookingCreate) => {
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const booking = await createBooking(payload);
      setSuccess(booking);
      return booking;
    } catch (e: unknown) {
      setError(normalizeApiError(e));
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setError(null);
    setSuccess(null);
  }, []);

  return { loading, error, success, submit, reset };
}
