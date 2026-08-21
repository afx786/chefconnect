from fastapi import FastAPI

from app.api.routes.chefs import router as chefs_router

app = FastAPI(title="ChefConnect")

app.include_router(chefs_router, prefix="/api/chefs", tags=["chefs"])
