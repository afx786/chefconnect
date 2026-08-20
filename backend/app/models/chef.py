from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Chef(Base):
    __tablename__ = "chefs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    cuisine: Mapped[str] = mapped_column(String(100), nullable=False)
    locality: Mapped[str] = mapped_column(String(100), nullable=False)
    rating: Mapped[Decimal] = mapped_column(Numeric(3, 2), nullable=False)
    price_per_meal: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    signature_dish: Mapped[str] = mapped_column(String(150), nullable=False)
    experience_years: Mapped[int] = mapped_column(Integer, nullable=False)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_available: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    dishes: Mapped[list["Dish"]] = relationship(
        back_populates="chef", cascade="all, delete-orphan"
    )
    bookings: Mapped[list["Booking"]] = relationship(back_populates="chef")