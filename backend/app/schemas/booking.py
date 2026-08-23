from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from app.models.booking import BookingStatus, MealSlot


class BookingCreate(BaseModel):
    chef_id: int = Field(gt=0)
    booking_date: date
    meal_slot: MealSlot
    special_requests: str | None = Field(default=None, max_length=500)

    @field_validator("booking_date")
    @classmethod
    def reject_past_dates(cls, v: date) -> date:
        if v < date.today():
            raise ValueError("booking_date cannot be in the past")
        return v

    @field_validator("special_requests")
    @classmethod
    def normalize_special_requests(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = v.strip()
        return v or None


class BookingChefOut(BaseModel):
    id: int
    name: str
    cuisine: str
    locality: str
    rating: Decimal
    price_per_meal: Decimal
    signature_dish: str

    model_config = {"from_attributes": True}


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
    chef: BookingChefOut

    model_config = {"from_attributes": True}


class BookingListResponse(BaseModel):
    bookings: list[BookingOut]
