from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.rate_limit import ip_chefs_limiter
from app.db.session import get_db
from app.schemas.chef import ChefListResponse
from app.services.chef_service import get_available_chefs

router = APIRouter()


@router.get(
    "",
    response_model=ChefListResponse,
    dependencies=[Depends(ip_chefs_limiter)],
)
def list_chefs(
    cuisine: Annotated[str | None, Query(max_length=100)] = None,
    locality: Annotated[str | None, Query(max_length=100)] = None,
    db: Session = Depends(get_db),
) -> ChefListResponse:
    chefs = get_available_chefs(db, cuisine=cuisine, locality=locality)
    return ChefListResponse(chefs=chefs)
