from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.rate_limit import booking_limiter
from app.db.session import get_db
from app.models.user import User
from app.schemas.booking import BookingCreate, BookingListResponse, BookingOut
from app.services.booking_service import create_booking, get_user_bookings

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
