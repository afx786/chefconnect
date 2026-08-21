import { useState, useCallback } from 'react';
import { Booking, BookingCreate } from '@/types/booking';
import { createBooking } from '@/services/bookingService';

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
    } catch (e: any) {
      const msg =
        e?.response?.data?.detail || e?.message || 'Booking failed';
      setError(msg);
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
