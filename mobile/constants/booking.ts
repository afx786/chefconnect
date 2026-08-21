export const MealSlots = ['BREAKFAST', 'LUNCH', 'DINNER'] as const;

export const MealSlotLabels: Record<string, string> = {
  BREAKFAST: 'Breakfast',
  LUNCH: 'Lunch',
  DINNER: 'Dinner',
};

export const BookingStatuses = ['PENDING', 'CONFIRMED', 'CHEF_EN_ROUTE'] as const;

export const BookingStatusLabels: Record<string, string> = {
  PENDING: 'Pending',
  CONFIRMED: 'Confirmed',
  CHEF_EN_ROUTE: 'Chef En Route',
};
