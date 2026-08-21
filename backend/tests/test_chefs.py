from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.api.routes.chefs import router as chefs_router
from app.db.database import Base
from app.db.session import get_db
from app.seed.seed_data import seed_database

app = FastAPI()
app.include_router(chefs_router, prefix="/api/chefs", tags=["chefs"])

_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(_engine, "connect")
def _set_sqlite_pragma(dbapi_conn, _connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


Base.metadata.create_all(bind=_engine)
_session = Session(bind=_engine)
seed_database(_session)
_session.close()


def _override_get_db():
    db = Session(bind=_engine)
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db
client = TestClient(app)


def test_get_all_available_chefs():
    resp = client.get("/api/chefs")
    assert resp.status_code == 200
    data = resp.json()
    assert "chefs" in data
    chefs = data["chefs"]
    assert len(chefs) > 0
    for chef in chefs:
        assert chef["is_available"] is True
        assert "dishes" in chef
        assert len(chef["dishes"]) > 0
        dish = chef["dishes"][0]
        assert "id" in dish
        assert "name" in dish
        assert "price" in dish
        assert "is_available" in dish


def test_cuisine_filter():
    resp = client.get("/api/chefs", params={"cuisine": "Indian"})
    assert resp.status_code == 200
    chefs = resp.json()["chefs"]
    assert len(chefs) > 0
    for chef in chefs:
        assert chef["cuisine"].lower() == "indian"


def test_locality_filter():
    resp = client.get("/api/chefs", params={"locality": "Noida"})
    assert resp.status_code == 200
    chefs = resp.json()["chefs"]
    assert len(chefs) > 0
    for chef in chefs:
        assert chef["locality"].lower() == "noida"


def test_case_insensitive_filter():
    resp = client.get("/api/chefs", params={"cuisine": "indian"})
    assert resp.status_code == 200
    chefs = resp.json()["chefs"]
    assert len(chefs) > 0
    for chef in chefs:
        assert chef["cuisine"].lower() == "indian"


def test_combined_filters():
    resp = client.get(
        "/api/chefs", params={"cuisine": "South Indian", "locality": "Noida"}
    )
    assert resp.status_code == 200
    chefs = resp.json()["chefs"]
    assert len(chefs) > 0
    for chef in chefs:
        assert chef["cuisine"].lower() == "south indian"
        assert chef["locality"].lower() == "noida"


def test_no_matching_chefs():
    resp = client.get("/api/chefs", params={"cuisine": "Martian"})
    assert resp.status_code == 200
    assert resp.json() == {"chefs": []}
