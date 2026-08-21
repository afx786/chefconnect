from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.chef import ChefListResponse
from app.services.chef_service import get_available_chefs

router = APIRouter()


@router.get("", response_model=ChefListResponse)
def list_chefs(
    cuisine: str | None = None,
    locality: str | None = None,
    db: Session = Depends(get_db),
) -> ChefListResponse:
    chefs = get_available_chefs(db, cuisine=cuisine, locality=locality)
    return ChefListResponse(chefs=chefs)
