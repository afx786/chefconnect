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

USER_A_EMAIL = "usera@bookinglist.example.com"
USER_A_PASS = "passA1234"
USER_B_EMAIL = "userb@bookinglist.example.com"
USER_B_PASS = "passB1234"
USER_C_EMAIL = "userc@bookinglist.example.com"
USER_C_PASS = "passC1234"

_user_a_id = _create_user(USER_A_EMAIL, USER_A_PASS, name="User A List")
_user_b_id = _create_user(USER_B_EMAIL, USER_B_PASS, name="User B List")
_user_c_id = _create_user(USER_C_EMAIL, USER_C_PASS, name="User C List")

_token_a = _login(USER_A_EMAIL, USER_A_PASS)
_token_b = _login(USER_B_EMAIL, USER_B_PASS)
_token_c = _login(USER_C_EMAIL, USER_C_PASS)

CHEF_ID = 5  # seeded chef


# ── Authentication / authorization ──────────────────────────────────


def test_list_bookings_missing_token_returns_401():
    resp = client.get("/api/bookings")
    assert resp.status_code == 401


def test_list_bookings_invalid_token_returns_401():
    resp = client.get(
        "/api/bookings",
        headers={"Authorization": "Bearer not-a-real-token"},
    )
    assert resp.status_code == 401


def test_list_bookings_with_valid_token_returns_200():
    resp = client.get("/api/bookings", headers=_auth_header(_token_c))
    assert resp.status_code == 200
    body = resp.json()
    assert "bookings" in body
    assert isinstance(body["bookings"], list)


def test_user_with_no_bookings_receives_empty_list():
    resp = client.get("/api/bookings", headers=_auth_header(_token_c))
    assert resp.status_code == 200
    assert resp.json() == {"bookings": []}


# ── User isolation ───────────────────────────────────────────────────


def test_users_only_see_their_own_bookings():
    created_a = client.post(
        "/api/bookings",
        json={
            "chef_id": CHEF_ID,
            "booking_date": "2026-10-01",
            "meal_slot": "DINNER",
        },
        headers=_auth_header(_token_a),
    )
    assert created_a.status_code == 201
    created_b = client.post(
        "/api/bookings",
        json={
            "chef_id": CHEF_ID,
            "booking_date": "2026-10-02",
            "meal_slot": "LUNCH",
        },
        headers=_auth_header(_token_b),
    )
    assert created_b.status_code == 201

    bookings_a = client.get("/api/bookings", headers=_auth_header(_token_a)).json()["bookings"]
    bookings_b = client.get("/api/bookings", headers=_auth_header(_token_b)).json()["bookings"]

    assert [b["id"] for b in bookings_a] == [created_a.json()["id"]]
    assert [b["id"] for b in bookings_b] == [created_b.json()["id"]]
    assert all(b["user_id"] == _user_a_id for b in bookings_a)
    assert all(b["user_id"] == _user_b_id for b in bookings_b)


def test_user_id_query_parameter_is_ignored_and_jwt_wins():
    resp = client.get(
        f"/api/bookings?user_id={_user_a_id}",
        headers=_auth_header(_token_b),
    )
    assert resp.status_code == 200
    bookings = resp.json()["bookings"]
    assert all(b["user_id"] == _user_b_id for b in bookings)


# ── Response shape ───────────────────────────────────────────────────


def test_booking_response_contains_status_and_chef_information():
    created = client.post(
        "/api/bookings",
        json={
            "chef_id": CHEF_ID,
            "booking_date": "2026-11-05",
            "meal_slot": "DINNER",
            "special_requests": "Mild spice.",
        },
        headers=_auth_header(_token_a),
    )
    assert created.status_code == 201

    bookings = client.get("/api/bookings", headers=_auth_header(_token_a)).json()["bookings"]
    booking = next(b for b in bookings if b["id"] == created.json()["id"])

    assert booking["status"] == "PENDING"
    assert booking["booking_date"] == "2026-11-05"
    assert booking["meal_slot"] == "DINNER"
    assert booking["special_requests"] == "Mild spice."
    assert booking["created_at"]
    assert booking["updated_at"]

    chef = booking["chef"]
    db_chef = (
        Session(bind=_engine).query(Chef).filter(Chef.id == CHEF_ID).first()
    )
    assert chef["id"] == CHEF_ID
    assert chef["name"] == db_chef.name
    assert chef["cuisine"] == db_chef.cuisine
    assert chef["locality"] == db_chef.locality
    assert float(chef["rating"]) == float(db_chef.rating)
    assert float(chef["price_per_meal"]) == float(db_chef.price_per_meal)
    assert chef["signature_dish"] == db_chef.signature_dish


def test_create_response_includes_chef_information():
    created = client.post(
        "/api/bookings",
        json={
            "chef_id": CHEF_ID,
            "booking_date": "2026-12-24",
            "meal_slot": "LUNCH",
        },
        headers=_auth_header(_token_a),
    )
    assert created.status_code == 201
    body = created.json()
    assert body["chef"]["id"] == CHEF_ID
    assert "name" in body["chef"]


def test_multiple_bookings_returned_for_user():
    first = client.post(
        "/api/bookings",
        json={"chef_id": CHEF_ID, "booking_date": "2027-01-01", "meal_slot": "LUNCH"},
        headers=_auth_header(_token_a),
    )
    second = client.post(
        "/api/bookings",
        json={"chef_id": CHEF_ID, "booking_date": "2027-01-02", "meal_slot": "DINNER"},
        headers=_auth_header(_token_a),
    )
    assert first.status_code == 201 and second.status_code == 201

    bookings = client.get("/api/bookings", headers=_auth_header(_token_a)).json()["bookings"]
    ids = {b["id"] for b in bookings}
    assert first.json()["id"] in ids
    assert second.json()["id"] in ids


def test_ordering_is_deterministic_newest_first():
    older = client.post(
        "/api/bookings",
        json={"chef_id": CHEF_ID, "booking_date": "2027-02-01", "meal_slot": "BREAKFAST"},
        headers=_auth_header(_token_a),
    )
    newer = client.post(
        "/api/bookings",
        json={"chef_id": CHEF_ID, "booking_date": "2027-02-02", "meal_slot": "DINNER"},
        headers=_auth_header(_token_a),
    )
    assert older.status_code == 201 and newer.status_code == 201

    bookings = client.get("/api/bookings", headers=_auth_header(_token_a)).json()["bookings"]
    ids = [b["id"] for b in bookings]
    assert len(ids) >= 2
    assert ids.index(newer.json()["id"]) < ids.index(older.json()["id"])
    assert ids == sorted(ids, reverse=True)


# ── Sensitive data leakage ───────────────────────────────────────────


def test_response_does_not_leak_password_or_sensitive_fields():
    resp = client.get("/api/bookings", headers=_auth_header(_token_a))
    raw = resp.text.lower()
    assert "password" not in raw
    for booking in resp.json()["bookings"]:
        assert "password_hash" not in booking
        assert set(booking.keys()) == {
            "id",
            "user_id",
            "chef_id",
            "booking_date",
            "meal_slot",
            "status",
            "special_requests",
            "created_at",
            "updated_at",
            "chef",
        }
        assert set(booking["chef"].keys()) == {
            "id",
            "name",
            "cuisine",
            "locality",
            "rating",
            "price_per_meal",
            "signature_dish",
        }
