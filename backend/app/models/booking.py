import enum
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class MealSlot(str, enum.Enum):
    BREAKFAST = "BREAKFAST"
    LUNCH = "LUNCH"
    DINNER = "DINNER"


class BookingStatus(str, enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CHEF_EN_ROUTE = "CHEF_EN_ROUTE"


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    chef_id: Mapped[int] = mapped_column(
        ForeignKey("chefs.id"), nullable=False, index=True
    )
    booking_date: Mapped[date] = mapped_column(Date, nullable=False)
    meal_slot: Mapped[MealSlot] = mapped_column(
        Enum(MealSlot, name="meal_slot", values_callable=lambda e: [m.value for m in e]),
        nullable=False,
    )
    status: Mapped[BookingStatus] = mapped_column(
        Enum(
            BookingStatus,
            name="booking_status",
            values_callable=lambda e: [s.value for s in e],
        ),
        nullable=False,
        default=BookingStatus.PENDING,
        server_default=BookingStatus.PENDING.value,
    )
    special_requests: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    user: Mapped["User"] = relationship(back_populates="bookings")
    chef: Mapped["Chef"] = relationship(back_populates="bookings")