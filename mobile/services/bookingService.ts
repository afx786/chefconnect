import api from './api';
import { BookingCreate, Booking } from '@/types/booking';

export async function createBooking(payload: BookingCreate): Promise<Booking> {
  const { data } = await api.post<Booking>('/api/bookings', payload);
  return data;
}
