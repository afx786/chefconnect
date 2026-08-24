from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.auth import router as auth_router
from app.api.routes.bookings import router as bookings_router
from app.api.routes.chefs import router as chefs_router
from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.seed.seed_data import seed_database


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    init_db()
    with SessionLocal() as session:
        seed_database(session)
    yield


app = FastAPI(title="ChefConnect", lifespan=lifespan)

app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(chefs_router, prefix="/api/chefs", tags=["chefs"])
app.include_router(bookings_router, prefix="/api/bookings", tags=["bookings"])
