from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.booking import BookingCreate, BookingOut
from app.services.booking_service import create_booking

router = APIRouter()


@router.post("", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
def create_new_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db),
) -> BookingOut:
    return create_booking(db, booking_data)
