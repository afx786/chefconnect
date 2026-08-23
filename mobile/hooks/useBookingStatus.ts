import { useEffect, useState } from 'react';
import { Booking, BookingStatus } from '@/types/booking';
import { bookingStatusSource } from '@/services/bookingStatusSource';

export function useBookingStatus(booking: Booking | null): BookingStatus | null {
  const [status, setStatus] = useState<BookingStatus | null>(
    booking ? booking.status : null,
  );

  useEffect(() => {
    if (!booking) {
      return undefined;
    }
    setStatus(booking.status);
    const unsubscribe = bookingStatusSource.subscribe(booking, setStatus);
    return unsubscribe;
  }, [booking]);

  return status;
}
