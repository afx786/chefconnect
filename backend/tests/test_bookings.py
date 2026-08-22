from datetime import datetime, timedelta, timezone

import jwt
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.api.routes.auth import router as auth_router
from app.api.routes.bookings import router as bookings_router
from app.core.config import settings
from app.core.security import hash_password
from app.db.database import Base
from app.db.session import get_db
from app.models import Chef
from app.models.user import User
from app.seed.seed_data import seed_database

app = FastAPI()
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
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


def _create_user(email, password, name="Test User"):
    db = Session(bind=_engine)
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        uid = existing.id
        db.close()
        return uid
    user = User(name=name, email=email, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    uid = user.id
    db.close()
    return uid


def _login(email, password):
    resp = client.post("/api/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def _auth_header(token):
    return {"Authorization": f"Bearer {token}"}


# ── Setup test users ────────────────────────────────────────────────

USER_A_EMAIL = "usera@bookings.example.com"
USER_A_PASS = "passA1234"
USER_B_EMAIL = "userb@bookings.example.com"
USER_B_PASS = "passB1234"

_user_a_id = _create_user(USER_A_EMAIL, USER_A_PASS, name="User A")
_user_b_id = _create_user(USER_B_EMAIL, USER_B_PASS, name="User B")

_token_a = _login(USER_A_EMAIL, USER_A_PASS)
_token_b = _login(USER_B_EMAIL, USER_B_PASS)

VALID_PAYLOAD = {
    "chef_id": 5,
    "booking_date": "2026-09-10",
    "meal_slot": "DINNER",
    "special_requests": "Less spicy food, please.",
}


# ── Authentication tests ────────────────────────────────────────────


def test_missing_auth_header_returns_401():
    resp = client.post("/api/bookings", json=VALID_PAYLOAD)
    assert resp.status_code == 401


def test_invalid_token_returns_401():
    resp = client.post(
        "/api/bookings",
        json=VALID_PAYLOAD,
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert resp.status_code == 401


def test_expired_token_returns_401():
    expire = datetime.now(timezone.utc) - timedelta(minutes=1)
    payload = {"sub": str(_user_a_id), "exp": expire}
    token = jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    resp = client.post(
        "/api/bookings", json=VALID_PAYLOAD, headers=_auth_header(token)
    )
    assert resp.status_code == 401


def test_malformed_token_returns_401():
    resp = client.post(
        "/api/bookings",
        json=VALID_PAYLOAD,
        headers={"Authorization": "Bearer not.a.jwt"},
    )
    assert resp.status_code == 401


def test_wrong_secret_token_returns_401():
    token = jwt.encode(
        {"sub": str(_user_a_id),
         "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
        "wrong-secret",
        algorithm="HS256",
    )
    resp = client.post(
        "/api/bookings", json=VALID_PAYLOAD, headers=_auth_header(token)
    )
    assert resp.status_code == 401


# ── Booking creation tests (authenticated) ──────────────────────────


def test_successful_booking_with_valid_jwt():
    resp = client.post(
        "/api/bookings", json=VALID_PAYLOAD, headers=_auth_header(_token_a)
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"] is not None
    assert data["user_id"] == _user_a_id
    assert data["chef_id"] == 5
    assert data["booking_date"] == "2026-09-10"
    assert data["meal_slot"] == "DINNER"
    assert data["status"] == "PENDING"
    assert data["special_requests"] == "Less spicy food, please."


def test_booking_status_is_pending():
    resp = client.post(
        "/api/bookings", json=VALID_PAYLOAD, headers=_auth_header(_token_a)
    )
    assert resp.status_code == 201
    assert resp.json()["status"] == "PENDING"


def test_booking_without_special_requests():
    payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "special_requests"}
    resp = client.post(
        "/api/bookings", json=payload, headers=_auth_header(_token_a)
    )
    assert resp.status_code == 201
    assert resp.json()["special_requests"] is None


def test_chef_does_not_exist():
    payload = {**VALID_PAYLOAD, "chef_id": 99999}
    resp = client.post(
        "/api/bookings", json=payload, headers=_auth_header(_token_a)
    )
    assert resp.status_code == 404


def test_chef_unavailable():
    session = Session(bind=_engine)
    chef = session.query(Chef).filter(Chef.id == 5).first()
    chef.is_available = False
    session.commit()
    session.close()

    resp = client.post(
        "/api/bookings", json=VALID_PAYLOAD, headers=_auth_header(_token_a)
    )
    assert resp.status_code == 400

    session = Session(bind=_engine)
    chef = session.query(Chef).filter(Chef.id == 5).first()
    chef.is_available = True
    session.commit()
    session.close()


def test_invalid_meal_slot():
    payload = {**VALID_PAYLOAD, "meal_slot": "BRUNCH"}
    resp = client.post(
        "/api/bookings", json=payload, headers=_auth_header(_token_a)
    )
    assert resp.status_code == 422


def test_missing_required_fields():
    resp = client.post("/api/bookings", json={}, headers=_auth_header(_token_a))
    assert resp.status_code == 422


def test_database_persistence():
    payload = {
        "chef_id": 6,
        "booking_date": "2026-09-11",
        "meal_slot": "LUNCH",
        "special_requests": "Jain food only.",
    }
    resp = client.post(
        "/api/bookings", json=payload, headers=_auth_header(_token_a)
    )
    assert resp.status_code == 201
    booking_id = resp.json()["id"]

    session = Session(bind=_engine)
    from app.models.booking import Booking

    booking = session.query(Booking).filter(Booking.id == booking_id).first()
    assert booking is not None
    assert booking.user_id == _user_a_id
    assert booking.chef_id == 6
    assert booking.status.value == "PENDING"
    session.close()


# ── User identity tests ─────────────────────────────────────────────


def test_booking_user_id_comes_from_jwt():
    resp = client.post(
        "/api/bookings", json=VALID_PAYLOAD, headers=_auth_header(_token_a)
    )
    assert resp.status_code == 201
    assert resp.json()["user_id"] == _user_a_id


def test_different_users_get_different_user_ids():
    resp_a = client.post(
        "/api/bookings", json=VALID_PAYLOAD, headers=_auth_header(_token_a)
    )
    resp_b = client.post(
        "/api/bookings", json=VALID_PAYLOAD, headers=_auth_header(_token_b)
    )
    assert resp_a.status_code == 201
    assert resp_b.status_code == 201
    assert resp_a.json()["user_id"] == _user_a_id
    assert resp_b.json()["user_id"] == _user_b_id
    assert resp_a.json()["user_id"] != resp_b.json()["user_id"]


def test_cannot_impersonate_other_user_via_body():
    payload = {**VALID_PAYLOAD, "user_id": _user_b_id}
    resp = client.post(
        "/api/bookings",
        json=payload,
        headers=_auth_header(_token_a),
    )
    assert resp.status_code == 201
    assert resp.json()["user_id"] == _user_a_id
    assert resp.json()["user_id"] != _user_b_id


def test_cannot_impersonate_nonexistent_user():
    payload = {**VALID_PAYLOAD, "user_id": 99999}
    resp = client.post(
        "/api/bookings",
        json=payload,
        headers=_auth_header(_token_a),
    )
    assert resp.status_code == 201
    assert resp.json()["user_id"] == _user_a_id
