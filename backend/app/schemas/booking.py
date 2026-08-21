from datetime import date, datetime

from pydantic import BaseModel

from app.models.booking import BookingStatus, MealSlot


class BookingCreate(BaseModel):
    chef_id: int
    user_id: int
    booking_date: date
    meal_slot: MealSlot
    special_requests: str | None = None


class BookingOut(BaseModel):
    id: int
    user_id: int
    chef_id: int
    booking_date: date
    meal_slot: MealSlot
    status: BookingStatus
    special_requests: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
