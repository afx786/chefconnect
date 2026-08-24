import { useEffect, useRef, useState } from 'react';
import { Booking, BookingStatus } from '@/types/booking';
import { bookingStatusSource } from '@/services/bookingStatusSource';
import { confirmBooking } from '@/services/bookingService';
import { statusAtLeast } from '@/utils/bookingStatus';

export function useBookingStatus(booking: Booking | null): BookingStatus | null {
  const [status, setStatus] = useState<BookingStatus | null>(
    booking ? booking.status : null,
  );
  const prevStatusRef = useRef<BookingStatus | null>(booking?.status ?? null);
  const prevBookingIdRef = useRef<number | null>(booking?.id ?? null);

  useEffect(() => {
    if (!booking) {
      return undefined;
    }

    if (booking.id !== prevBookingIdRef.current) {
      prevBookingIdRef.current = booking.id;
      prevStatusRef.current = booking.status;
    }

    setStatus(booking.status);

    const unsubscribe = bookingStatusSource.subscribe(booking, (newStatus) => {
      setStatus(newStatus);

      const crossedConfirmed =
        !statusAtLeast(prevStatusRef.current ?? 'PENDING', 'CONFIRMED') &&
        statusAtLeast(newStatus, 'CONFIRMED');

      prevStatusRef.current = newStatus;

      if (crossedConfirmed && booking.status === 'PENDING') {
        confirmBooking(booking.id).catch(() => {});
      }
    });

    return unsubscribe;
  }, [booking]);

  return status;
}
