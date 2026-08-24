import logging

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.booking import Booking, BookingStatus
from app.models.chef import Chef
from app.models.user import User
from app.schemas.booking import BookingCreate
from app.services.webhook_service import emit_booking_confirmed

logger = logging.getLogger(__name__)


def create_booking(db: Session, data: BookingCreate, user: User) -> Booking:
    chef = db.query(Chef).filter(Chef.id == data.chef_id).first()
    if not chef:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chef with id {data.chef_id} not found",
        )

    if not chef.is_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Chef with id {data.chef_id} is currently unavailable",
        )

    booking = Booking(
        user_id=user.id,
        chef_id=data.chef_id,
        booking_date=data.booking_date,
        meal_slot=data.meal_slot,
        status=BookingStatus.PENDING,
        special_requests=data.special_requests,
    )

    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


def get_user_bookings(db: Session, user: User) -> list[Booking]:
    stmt = (
        select(Booking)
        .where(Booking.user_id == user.id)
        .options(selectinload(Booking.chef))
        .order_by(Booking.created_at.desc(), Booking.id.desc())
    )
    return list(db.scalars(stmt).all())


def confirm_booking(db: Session, booking: Booking, user: User) -> Booking:
    if booking.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )
    if booking.status != BookingStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Booking is not pending confirmation",
        )

    should_emit = not booking.confirmed_event_emitted
    logger.info(
        "CONFIRM_TRACE booking=%d status=%s already_emitted=%s should_emit=%s",
        booking.id, booking.status.value, booking.confirmed_event_emitted, should_emit,
    )
    booking.status = BookingStatus.CONFIRMED
    booking.confirmed_event_emitted = True
    db.commit()
    db.refresh(booking)

    if should_emit:
        emit_booking_confirmed(
            booking_id=booking.id,
            user_id=user.id,
            user_email=user.email,
            user_name=user.name,
            chef_name=booking.chef.name,
            booking_date=str(booking.booking_date),
            meal_slot=booking.meal_slot.value,
        )

    return booking
