export interface Dish {
  id: number;
  name: string;
  description: string | null;
  price: number;
  is_available: boolean;
}

export interface Chef {
  id: number;
  name: string;
  cuisine: string;
  locality: string;
  rating: number;
  price_per_meal: number;
  signature_dish: string;
  experience_years: number;
  bio: string | null;
  is_available: boolean;
  dishes: Dish[];
}

export interface ChefListResponse {
  chefs: Chef[];
}
