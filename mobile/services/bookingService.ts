import api from './api';
import { BookingCreate, Booking, BookingListResponse } from '@/types/booking';

export async function createBooking(payload: BookingCreate): Promise<Booking> {
  const { data } = await api.post<Booking>('/api/bookings', payload);
  return data;
}

export async function getBookings(): Promise<Booking[]> {
  const { data } = await api.get<BookingListResponse>('/api/bookings');
  return data.bookings;
}

export async function confirmBooking(bookingId: number): Promise<Booking> {
  const { data } = await api.post<Booking>(`/api/bookings/${bookingId}/confirm`);
  return data;
}
