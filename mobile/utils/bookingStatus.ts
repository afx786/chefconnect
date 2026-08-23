import { BookingStatus } from '@/types/booking';

// Explicit lifecycle ordering. Never rely on alphabetical ordering.
export const STATUS_ORDER: Record<BookingStatus, number> = {
  PENDING: 0,
  CONFIRMED: 1,
  CHEF_EN_ROUTE: 2,
};

export function statusAtLeast(current: BookingStatus, minimum: BookingStatus): boolean {
  return STATUS_ORDER[current] >= STATUS_ORDER[minimum];
}

export function maxStatus(a: BookingStatus, b: BookingStatus): BookingStatus {
  return STATUS_ORDER[a] >= STATUS_ORDER[b] ? a : b;
}
