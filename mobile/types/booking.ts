export type MealSlot = 'BREAKFAST' | 'LUNCH' | 'DINNER';

export type BookingStatus = 'PENDING' | 'CONFIRMED' | 'CHEF_EN_ROUTE';

export interface BookingCreate {
  chef_id: number;
  booking_date: string;
  meal_slot: MealSlot;
  special_requests?: string | null;
}

export interface BookingChef {
  id: number;
  name: string;
  cuisine: string;
  locality: string;
  rating: number;
  price_per_meal: number;
  signature_dish: string;
}

export interface Booking {
  id: number;
  user_id: number;
  chef_id: number;
  booking_date: string;
  meal_slot: MealSlot;
  status: BookingStatus;
  special_requests: string | null;
  created_at: string;
  updated_at: string;
  chef: BookingChef;
}

export interface BookingListResponse {
  bookings: Booking[];
}
