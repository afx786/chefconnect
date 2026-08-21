from fastapi import FastAPI

from app.api.routes.bookings import router as bookings_router
from app.api.routes.chefs import router as chefs_router

app = FastAPI(title="ChefConnect")

app.include_router(chefs_router, prefix="/api/chefs", tags=["chefs"])
app.include_router(bookings_router, prefix="/api/bookings", tags=["bookings"])
