from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select

from app.api.deps import get_current_user
from app.core.rate_limit import booking_limiter
from app.db.session import get_db
from app.models.booking import Booking
from app.models.user import User
from app.schemas.booking import BookingCreate, BookingListResponse, BookingOut
from app.services.booking_service import create_booking, get_user_bookings, confirm_booking

router = APIRouter()


@router.get("", response_model=BookingListResponse)
def list_my_bookings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BookingListResponse:
    return BookingListResponse(bookings=get_user_bookings(db, current_user))


@router.post(
    "",
    response_model=BookingOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(booking_limiter)],
)
def create_new_booking(
    booking_data: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BookingOut:
    return create_booking(db, booking_data, current_user)


@router.post(
    "/{booking_id}/confirm",
    response_model=BookingOut,
    dependencies=[Depends(booking_limiter)],
)
def confirm_booking_endpoint(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BookingOut:
    stmt = (
        select(Booking)
        .where(Booking.id == booking_id)
        .options(selectinload(Booking.chef))
    )
    booking = db.scalars(stmt).first()
    if not booking:
        from fastapi import HTTPException
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    return confirm_booking(db, booking, current_user)
