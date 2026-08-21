from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.api.routes.bookings import router as bookings_router
from app.db.database import Base
from app.db.session import get_db
from app.models import Chef
from app.seed.seed_data import seed_database

app = FastAPI()
app.include_router(bookings_router, prefix="/api/bookings", tags=["bookings"])

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

VALID_PAYLOAD = {
    "chef_id": 5,
    "user_id": 4,
    "booking_date": "2026-09-10",
    "meal_slot": "DINNER",
    "special_requests": "Less spicy food, please.",
}


def test_successful_booking_creation():
    resp = client.post("/api/bookings", json=VALID_PAYLOAD)
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"] is not None
    assert data["user_id"] == 4
    assert data["chef_id"] == 5
    assert data["booking_date"] == "2026-09-10"
    assert data["meal_slot"] == "DINNER"
    assert data["status"] == "PENDING"
    assert data["special_requests"] == "Less spicy food, please."


def test_user_does_not_exist():
    payload = {**VALID_PAYLOAD, "user_id": 99999}
    resp = client.post("/api/bookings", json=payload)
    assert resp.status_code == 404


def test_chef_does_not_exist():
    payload = {**VALID_PAYLOAD, "chef_id": 99999}
    resp = client.post("/api/bookings", json=payload)
    assert resp.status_code == 404


def test_chef_unavailable():
    session = Session(bind=_engine)
    chef = session.query(Chef).filter(Chef.id == 5).first()
    chef.is_available = False
    session.commit()
    session.close()

    payload = {**VALID_PAYLOAD, "chef_id": 5}
    resp = client.post("/api/bookings", json=payload)
    assert resp.status_code == 400

    session = Session(bind=_engine)
    chef = session.query(Chef).filter(Chef.id == 5).first()
    chef.is_available = True
    session.commit()
    session.close()


def test_invalid_meal_slot():
    payload = {**VALID_PAYLOAD, "meal_slot": "BRUNCH"}
    resp = client.post("/api/bookings", json=payload)
    assert resp.status_code == 422


def test_missing_required_fields():
    resp = client.post("/api/bookings", json={})
    assert resp.status_code == 422


def test_no_special_requests():
    payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "special_requests"}
    resp = client.post("/api/bookings", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["special_requests"] is None


def test_database_persistence():
    payload = {
        "chef_id": 6,
        "user_id": 5,
        "booking_date": "2026-09-11",
        "meal_slot": "LUNCH",
        "special_requests": "Jain food only.",
    }
    resp = client.post("/api/bookings", json=payload)
    assert resp.status_code == 201
    booking_id = resp.json()["id"]

    session = Session(bind=_engine)
    from app.models.booking import Booking

    booking = session.query(Booking).filter(Booking.id == booking_id).first()
    assert booking is not None
    assert booking.user_id == 5
    assert booking.chef_id == 6
    assert booking.status.value == "PENDING"
    session.close()
