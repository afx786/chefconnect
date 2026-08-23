from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.chef import Chef

MAX_FILTER_LENGTH = 100


def normalize_filter(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    return value[:MAX_FILTER_LENGTH]


def get_available_chefs(
    session: Session,
    *,
    cuisine: str | None = None,
    locality: str | None = None,
) -> list[Chef]:
    cuisine = normalize_filter(cuisine)
    locality = normalize_filter(locality)

    stmt = (
        select(Chef)
        .where(Chef.is_available == True)  # noqa: E712
        .options(selectinload(Chef.dishes))
    )

    if cuisine:
        stmt = stmt.where(func.lower(Chef.cuisine) == cuisine.lower())

    if locality:
        stmt = stmt.where(func.lower(Chef.locality) == locality.lower())

    return list(session.execute(stmt).scalars().all())
