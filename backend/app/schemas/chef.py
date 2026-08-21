from decimal import Decimal

from pydantic import BaseModel


class DishOut(BaseModel):
    id: int
    name: str
    description: str | None
    price: Decimal
    is_available: bool

    model_config = {"from_attributes": True}


class ChefOut(BaseModel):
    id: int
    name: str
    cuisine: str
    locality: str
    rating: Decimal
    price_per_meal: Decimal
    signature_dish: str
    experience_years: int
    bio: str | None
    is_available: bool
    dishes: list[DishOut]

    model_config = {"from_attributes": True}


class ChefListResponse(BaseModel):
    chefs: list[ChefOut]
