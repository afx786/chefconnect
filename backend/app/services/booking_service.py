from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.booking import Booking, BookingStatus
from app.models.chef import Chef
from app.models.user import User
from app.schemas.booking import BookingCreate


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
