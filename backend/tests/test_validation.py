from datetime import date, timedelta

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.api.routes.auth import router as auth_router
from app.api.routes.bookings import router as bookings_router
from app.api.routes.chefs import router as chefs_router
from app.core.security import hash_password
from app.db.database import Base
from app.db.session import get_db
from app.models.user import User
from app.seed.seed_data import seed_database

app = FastAPI()
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(chefs_router, prefix="/api/chefs", tags=["chefs"])
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


# ── Helpers ──────────────────────────────────────────────────────────


def _create_user(email, password="StrongPass123", name="Validation User"):
    db = Session(bind=_engine)
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        db.close()
        return
    user = User(name=name, email=email, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()


def _signup(email="validation@example.com", password="StrongPass123", name="Validation User"):
    return client.post(
        "/api/auth/signup",
        json={"name": name, "email": email, "password": password},
    )


def _login_token(email="validation@example.com", password="StrongPass123"):
    _create_user(email, password)
    response = client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


FUTURE_DATE = (date.today() + timedelta(days=7)).isoformat()


def _booking_payload(**overrides):
    payload = {
        "chef_id": 1,
        "booking_date": FUTURE_DATE,
        "meal_slot": "DINNER",
        "special_requests": None,
    }
    payload.update(overrides)
    return payload


# ── Signup validation ────────────────────────────────────────────────


def test_signup_accepts_valid_input():
    response = _signup()
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Validation User"
    assert data["email"] == "validation@example.com"


def test_signup_rejects_blank_name():
    response = _signup(email="blank@example.com", name="   ")
    assert response.status_code == 422


def test_signup_rejects_overlong_name():
    response = _signup(email="long@example.com", name="x" * 101)
    assert response.status_code == 422


def test_signup_rejects_short_password():
    response = _signup(email="shortpw@example.com", password="short")
    assert response.status_code == 422


def test_signup_normalizes_email_case_and_whitespace():
    response = _signup(email="  MixedCase@Example.COM ", name="Email Case")
    assert response.status_code == 201
    assert response.json()["email"] == "mixedcase@example.com"


def test_login_with_different_email_case_succeeds():
    _signup(email="casecheck@example.com", password="StrongPass123", name="Case Check")
    response = client.post(
        "/api/auth/login",
        json={"email": "  CASECHECK@EXAMPLE.com ", "password": "StrongPass123"},
    )
    assert response.status_code == 200


# ── Booking validation ───────────────────────────────────────────────


def test_booking_chef_id_must_be_positive():
    headers = _login_token()
    for bad_id in (0, -5):
        response = client.post(
            "/api/bookings",
            json=_booking_payload(chef_id=bad_id),
            headers=headers,
        )
        assert response.status_code == 422


def test_booking_rejects_past_date():
    headers = _login_token()
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    response = client.post(
        "/api/bookings",
        json=_booking_payload(booking_date=yesterday),
        headers=headers,
    )
    assert response.status_code == 422


def test_booking_rejects_invalid_meal_slot():
    headers = _login_token()
    response = client.post(
        "/api/bookings",
        json=_booking_payload(meal_slot="BRUNCH"),
        headers=headers,
    )
    assert response.status_code == 422


def test_booking_special_requests_length_cap():
    headers = _login_token()
    response = client.post(
        "/api/bookings",
        json=_booking_payload(special_requests="x" * 501),
        headers=headers,
    )
    assert response.status_code == 422


def test_booking_special_requests_whitespace_only_becomes_none():
    headers = _login_token(email="wsbook@example.com")
    response = client.post(
        "/api/bookings",
        json=_booking_payload(special_requests="   "),
        headers=headers,
    )
    assert response.status_code == 201
    assert response.json()["special_requests"] is None


def test_booking_special_requests_is_trimmed():
    headers = _login_token(email="trimbook@example.com")
    response = client.post(
        "/api/bookings",
        json=_booking_payload(special_requests="  No cilantro please  "),
        headers=headers,
    )
    assert response.status_code == 201
    assert response.json()["special_requests"] == "No cilantro please"


# ── Chef filter validation ───────────────────────────────────────────


def test_chef_filters_remain_case_insensitive():
    response = client.get("/api/chefs", params={"cuisine": "indian"})
    assert response.status_code == 200
    chefs = response.json()["chefs"]
    assert len(chefs) > 0


def test_chef_filters_blank_value_treated_as_no_filter():
    all_chefs = client.get("/api/chefs").json()["chefs"]
    filtered = client.get("/api/chefs", params={"cuisine": "   "}).json()["chefs"]
    assert len(filtered) == len(all_chefs)


def test_chef_filters_reject_oversized_input():
    response = client.get("/api/chefs", params={"cuisine": "x" * 150})
    assert response.status_code == 422


def test_booking_body_user_id_cannot_override_identity():
    headers = _login_token(email="impersonate-check@example.com")
    response = client.post(
        "/api/bookings",
        json={**_booking_payload(), "user_id": 999},
        headers=headers,
    )
    assert response.status_code == 201
    assert response.json()["user_id"] != 999


def test_password_hash_still_not_exposed_by_validation_changes():
    response = _signup(email="nohash@example.com")
    assert "password" not in response.json()
    assert "password_hash" not in response.json()
