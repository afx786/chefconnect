from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.booking import BookingCreate, BookingOut
from app.services.booking_service import create_booking

router = APIRouter()


@router.post("", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
def create_new_booking(
    booking_data: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BookingOut:
    return create_booking(db, booking_data, current_user)
