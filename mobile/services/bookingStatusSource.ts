import { Booking, BookingStatus } from '@/types/booking';
import { maxStatus } from '@/utils/bookingStatus';

// Simulated progression windows (seconds after booking.created_at).
// Deterministic: the displayed status is derived from created_at and the
// current time, so leaving and reopening the tracker never restarts it.
export const CONFIRMED_AFTER_SECONDS = 10;
export const EN_ROUTE_AFTER_SECONDS = 20;
const TICK_MS = 1000;

export type BookingStatusListener = (status: BookingStatus) => void;

/**
 * Source of the status shown by the Booking Tracker.
 * The tracker consumes statuses through this interface only, so a future
 * RealTimeBookingStatusSource (polling / WebSocket / SSE) can replace the
 * simulation without touching any UI code.
 */
export interface BookingStatusSource {
  subscribe(booking: Booking, listener: BookingStatusListener): () => void;
}

function simulatedStatusAt(createdAtMs: number, nowMs: number): BookingStatus {
  const elapsedSeconds = (nowMs - createdAtMs) / 1000;
  if (elapsedSeconds >= EN_ROUTE_AFTER_SECONDS) {
    return 'CHEF_EN_ROUTE';
  }
  if (elapsedSeconds >= CONFIRMED_AFTER_SECONDS) {
    return 'CONFIRMED';
  }
  return 'PENDING';
}

/**
 * MVP simulation. The backend persisted status is server-owned and acts as a
 * floor: the simulation may advance the displayed status over time but can
 * never regress below it (e.g. a persisted CONFIRMED booking never shows
 * PENDING). The mobile app never writes status changes back to the API.
 */
export class SimulatedBookingStatusSource implements BookingStatusSource {
  subscribe(booking: Booking, listener: BookingStatusListener): () => void {
    const createdAtMs = new Date(booking.created_at).getTime();
    let lastEmitted: BookingStatus | null = null;

    const emit = () => {
      const next = maxStatus(simulatedStatusAt(createdAtMs, Date.now()), booking.status);
      if (next !== lastEmitted) {
        lastEmitted = next;
        listener(next);
      }
    };

    emit();
    const intervalId = setInterval(emit, TICK_MS);

    return () => {
      clearInterval(intervalId);
    };
  }
}

export const bookingStatusSource: BookingStatusSource = new SimulatedBookingStatusSource();
