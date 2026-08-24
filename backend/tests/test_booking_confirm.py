from unittest.mock import patch, MagicMock

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


def _create_booking(token):
    resp = client.post(
        "/api/bookings",
        json={
            "chef_id": 5,
            "booking_date": "2026-12-01",
            "meal_slot": "DINNER",
        },
        headers=_auth_header(token),
    )
    assert resp.status_code == 201
    return resp.json()


# ── Setup ────────────────────────────────────────────────────────────

USER_A_EMAIL = "confirma@booking.example.com"
USER_A_PASS = "passA1234"
USER_B_EMAIL = "confirmb@booking.example.com"
USER_B_PASS = "passB1234"
USER_C_EMAIL = "confirmc@booking.example.com"
USER_C_PASS = "passC1234"

_user_a_id = _create_user(USER_A_EMAIL, USER_A_PASS, name="User A Confirm")
_user_b_id = _create_user(USER_B_EMAIL, USER_B_PASS, name="User B Confirm")
_user_c_id = _create_user(USER_C_EMAIL, USER_C_PASS, name="User C Confirm")

_token_a = _login(USER_A_EMAIL, USER_A_PASS)
_token_b = _login(USER_B_EMAIL, USER_B_PASS)
_token_c = _login(USER_C_EMAIL, USER_C_PASS)

CHEF_ID = 5


# ── 1. Authenticated user can confirm own PENDING booking ───────────


def test_authenticated_user_can_confirm_own_pending_booking():
    booking = _create_booking(_token_a)
    with patch("app.services.booking_service.emit_booking_confirmed"):
        resp = client.post(
            f"/api/bookings/{booking['id']}/confirm",
            headers=_auth_header(_token_a),
        )
    assert resp.status_code == 200
    assert resp.json()["status"] == "CONFIRMED"


# ── 2. Unauthenticated user cannot confirm ──────────────────────────


def test_unauthenticated_user_cannot_confirm():
    booking = _create_booking(_token_a)
    resp = client.post(f"/api/bookings/{booking['id']}/confirm")
    assert resp.status_code == 401


def test_invalid_token_cannot_confirm():
    booking = _create_booking(_token_a)
    resp = client.post(
        f"/api/bookings/{booking['id']}/confirm",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert resp.status_code == 401


# ── 3. User cannot confirm another user's booking ──────────────────


def test_user_cannot_confirm_another_users_booking():
    booking = _create_booking(_token_a)
    resp = client.post(
        f"/api/bookings/{booking['id']}/confirm",
        headers=_auth_header(_token_b),
    )
    assert resp.status_code == 404


# ── 4. PENDING → CONFIRMED is persisted ─────────────────────────────


def test_pending_to_confirmed_is_persisted():
    booking = _create_booking(_token_a)
    with patch("app.services.booking_service.emit_booking_confirmed"):
        client.post(
            f"/api/bookings/{booking['id']}/confirm",
            headers=_auth_header(_token_a),
        )
    db = Session(bind=_engine)
    from app.models.booking import Booking
    db_booking = db.query(Booking).filter(Booking.id == booking["id"]).first()
    assert db_booking.status.value == "CONFIRMED"
    assert db_booking.confirmed_event_emitted is True
    db.close()


# ── 5. Repeated confirmation does not regress status ────────────────


def test_repeated_confirmation_does_not_regress_status():
    booking = _create_booking(_token_a)
    with patch("app.services.booking_service.emit_booking_confirmed"):
        client.post(
            f"/api/bookings/{booking['id']}/confirm",
            headers=_auth_header(_token_a),
        )
    resp = client.post(
        f"/api/bookings/{booking['id']}/confirm",
        headers=_auth_header(_token_a),
    )
    assert resp.status_code == 409
    assert "not pending" in resp.json()["detail"].lower()


# ── 6. Repeated confirmation does not emit second event ─────────────


def test_repeated_confirmation_does_not_emit_second_event():
    booking = _create_booking(_token_a)
    with patch("app.services.booking_service.emit_booking_confirmed") as mock_emit:
        client.post(
            f"/api/bookings/{booking['id']}/confirm",
            headers=_auth_header(_token_a),
        )
        first_call_count = mock_emit.call_count
        client.post(
            f"/api/bookings/{booking['id']}/confirm",
            headers=_auth_header(_token_a),
        )
    assert first_call_count == 1
    assert mock_emit.call_count == 1


# ── 7. Event payload contains required fields ───────────────────────


def test_event_payload_contains_required_fields():
    booking = _create_booking(_token_a)
    with patch("app.services.booking_service.emit_booking_confirmed") as mock_emit:
        client.post(
            f"/api/bookings/{booking['id']}/confirm",
            headers=_auth_header(_token_a),
        )
    assert mock_emit.call_count == 1
    kwargs = mock_emit.call_args[1]
    assert kwargs["booking_id"] == booking["id"]
    assert kwargs["user_id"] == _user_a_id
    assert kwargs["user_email"] == USER_A_EMAIL
    assert kwargs["user_name"] == "User A Confirm"
    assert "chef_name" in kwargs
    assert kwargs["booking_date"] == "2026-12-01"
    assert kwargs["meal_slot"] == "DINNER"


# ── 8. Password hash is never included ──────────────────────────────


def test_password_hash_never_included_in_event():
    booking = _create_booking(_token_a)
    with patch("app.services.booking_service.emit_booking_confirmed") as mock_emit:
        client.post(
            f"/api/bookings/{booking['id']}/confirm",
            headers=_auth_header(_token_a),
        )
    kwargs = mock_emit.call_args[1]
    assert "password_hash" not in kwargs
    assert "password" not in kwargs


# ── 9. JWT is never included ────────────────────────────────────────


def test_jwt_never_included_in_event():
    booking = _create_booking(_token_a)
    with patch("app.services.booking_service.emit_booking_confirmed") as mock_emit:
        client.post(
            f"/api/bookings/{booking['id']}/confirm",
            headers=_auth_header(_token_a),
        )
    kwargs = mock_emit.call_args[1]
    assert "jwt" not in kwargs
    assert "token" not in kwargs
    assert "access_token" not in kwargs


# ── 10. Webhook is called only after successful confirmation ────────


def test_webhook_called_only_after_successful_confirmation():
    booking = _create_booking(_token_a)
    with patch("app.services.booking_service.emit_booking_confirmed") as mock_emit:
        client.post(
            f"/api/bookings/{booking['id']}/confirm",
            headers=_auth_header(_token_b),
        )
        assert mock_emit.call_count == 0
        client.post(
            f"/api/bookings/{booking['id']}/confirm",
            headers=_auth_header(_token_a),
        )
        assert mock_emit.call_count == 1


# ── 11. Webhook failure does not corrupt database state ─────────────


def test_webhook_failure_does_not_corrupt_database_state():
    booking = _create_booking(_token_a)
    with patch.object(settings, "N8N_BOOKING_CONFIRMED_WEBHOOK_URL", "https://n8n.test/webhook"):
        with patch("app.services.webhook_service.httpx") as mock_httpx:
            mock_httpx.post.side_effect = Exception("webhook down")
            resp = client.post(
                f"/api/bookings/{booking['id']}/confirm",
                headers=_auth_header(_token_a),
            )
    assert resp.status_code == 200
    assert resp.json()["status"] == "CONFIRMED"
    db = Session(bind=_engine)
    from app.models.booking import Booking
    db_booking = db.query(Booking).filter(Booking.id == booking["id"]).first()
    assert db_booking.status.value == "CONFIRMED"
    db.close()


# ── 12. Non-PENDING booking cannot be reconfirmed ───────────────────


def test_non_pending_booking_cannot_be_reconfirmed():
    booking = _create_booking(_token_a)
    with patch("app.services.booking_service.emit_booking_confirmed"):
        client.post(
            f"/api/bookings/{booking['id']}/confirm",
            headers=_auth_header(_token_a),
        )
    resp = client.post(
        f"/api/bookings/{booking['id']}/confirm",
        headers=_auth_header(_token_a),
    )
    assert resp.status_code == 409


# ── 13. Non-existent booking returns 404 ────────────────────────────


def test_non_existent_booking_returns_404():
    resp = client.post(
        "/api/bookings/99999/confirm",
        headers=_auth_header(_token_a),
    )
    assert resp.status_code == 404


# ── 14. Webhook service respects environment variable ───────────────


def test_webhook_not_called_when_url_not_configured():
    booking = _create_booking(_token_a)
    with patch.object(settings, "N8N_BOOKING_CONFIRMED_WEBHOOK_URL", ""):
        with patch("app.services.webhook_service.httpx") as mock_httpx:
            client.post(
                f"/api/bookings/{booking['id']}/confirm",
                headers=_auth_header(_token_a),
            )
            mock_httpx.post.assert_not_called()


# ── 15. Webhook called with correct URL when configured ─────────────


def test_webhook_called_with_correct_url():
    booking = _create_booking(_token_a)
    with patch.object(settings, "N8N_BOOKING_CONFIRMED_WEBHOOK_URL", "https://n8n.test/webhook"):
        with patch("app.services.webhook_service.httpx") as mock_httpx:
            mock_httpx.post.return_value = MagicMock(status_code=200)
            client.post(
                f"/api/bookings/{booking['id']}/confirm",
                headers=_auth_header(_token_a),
            )
            mock_httpx.post.assert_called_once()
            call_args = mock_httpx.post.call_args
            assert call_args[0][0] == "https://n8n.test/webhook"
            payload = call_args[1]["json"]
            assert payload["event"] == "booking.confirmed"
            assert payload["booking_id"] == booking["id"]
            assert payload["status"] == "CONFIRMED"
