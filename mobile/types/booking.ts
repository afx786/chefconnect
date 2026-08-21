export type MealSlot = 'BREAKFAST' | 'LUNCH' | 'DINNER';

export type BookingStatus = 'PENDING' | 'CONFIRMED' | 'CHEF_EN_ROUTE';

export interface BookingCreate {
  chef_id: number;
  user_id: number;
  booking_date: string;
  meal_slot: MealSlot;
  special_requests?: string | null;
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
}
