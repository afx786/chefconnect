import time

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fakeredis import FakeRedis
from redis import RedisError
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
import app.cache.redis as cache_redis
from app.api.routes.auth import router as auth_router
from app.api.routes.bookings import router as bookings_router
from app.api.routes.chefs import router as chefs_router
from app.core import rate_limit as rate_limit_module
from app.core.config import settings
from app.core.security import hash_password
from app.db.database import Base
from app.db.session import get_db
from app.models.user import User
from app.seed.seed_data import seed_database


class FakeIPMiddleware:
    """Lets tests simulate different client IPs via the X-Test-IP header."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = dict(scope.get("headers", []))
            ip = headers.get(b"x-test-ip", b"10.0.0.1").decode()
            scope["client"] = (ip, 12345)
        await self.app(scope, receive, send)


def _build_app():
    test_app = FastAPI()
    test_app.add_middleware(FakeIPMiddleware)
    test_app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
    test_app.include_router(chefs_router, prefix="/api/chefs", tags=["chefs"])
    test_app.include_router(bookings_router, prefix="/api/bookings", tags=["bookings"])

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _pragma(dbapi_conn, _record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=engine)
    session = Session(bind=engine)
    seed_database(session)
    session.close()

    def override_get_db():
        db = Session(bind=engine)
        try:
            yield db
        finally:
            db.close()

    test_app.dependency_overrides[get_db] = override_get_db
    return test_app, engine


@pytest.fixture()
def limited_client(monkeypatch):
    fake_client = FakeRedis(decode_responses=True)
    monkeypatch.setattr(cache_redis, "_client", fake_client)
    monkeypatch.setattr(settings, "RATE_LIMIT_ENABLED", True)
    monkeypatch.setattr(settings, "RATE_LIMIT_WINDOW_SECONDS", 60)
    monkeypatch.setattr(settings, "RATE_LIMIT_AUTH_MAX_REQUESTS", 3)
    monkeypatch.setattr(settings, "RATE_LIMIT_BOOKINGS_MAX_REQUESTS", 2)
    monkeypatch.setattr(settings, "RATE_LIMIT_CHEFS_MAX_REQUESTS", 5)
    test_app, _engine = _build_app()
    return TestClient(test_app)


def _signup(client, email, password="StrongPass123"):
    return client.post(
        "/api/auth/signup",
        json={"name": "Rate Test", "email": email, "password": password},
    )


def _login(client, email="ratelimit@example.com", password="StrongPass123", ip="10.0.0.1"):
    return client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
        headers={"X-Test-IP": ip},
    )


def _token_header(response):
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


# ── Auth rate limiting (critical, IP-scoped) ─────────────────────────


def test_requests_below_limit_are_allowed(limited_client):
    for _ in range(3):
        response = _login(limited_client)
        assert response.status_code == 401  # unknown user, but not rate limited


def test_exceeding_auth_limit_returns_429_with_retry_after(limited_client):
    _signup(limited_client, "ratelimit@example.com")
    assert _login(limited_client).status_code == 200
    assert _login(limited_client).status_code == 200

    third = _login(limited_client)
    assert third.status_code == 429
    assert "Retry-After" in third.headers
    assert int(third.headers["Retry-After"]) >= 1
    assert third.headers["X-RateLimit-Limit"] == "3"
    assert third.headers["X-RateLimit-Remaining"] == "0"
    assert third.json()["detail"] == "Too many requests, please try again later"


def test_rate_limit_headers_present_on_allowed_request(limited_client):
    _signup(limited_client, "ratelimit@example.com")
    response = _login(limited_client)
    assert response.headers["X-RateLimit-Limit"] == "3"
    assert int(response.headers["X-RateLimit-Remaining"]) == 1
    assert int(response.headers["X-RateLimit-Reset"]) > int(time.time())


def test_separate_clients_have_separate_limits(limited_client):
    _signup(limited_client, "ratelimit@example.com")
    assert _login(limited_client, ip="10.0.0.1").status_code == 200
    assert _login(limited_client, ip="10.0.0.1").status_code == 200
    assert _login(limited_client, ip="10.0.0.1").status_code == 429
    assert _login(limited_client, ip="10.0.0.2").status_code == 200


def test_rate_limit_key_has_ttl_and_resets_in_new_window(limited_client, monkeypatch):
    _signup(limited_client, "ratelimit@example.com")
    _login(limited_client)

    fake: FakeRedis = cache_redis._client
    keys = [k for k in fake.keys("ratelimit:*") if ":auth:" in k]
    assert len(keys) == 1
    ttl = fake.ttl(keys[0])
    assert 0 < ttl <= 60

    real_time = time.time
    monkeypatch.setattr(
        rate_limit_module.time,
        "time",
        lambda: real_time() + 61,
    )
    next_window_response = _login(limited_client)
    assert next_window_response.status_code == 200
    assert int(next_window_response.headers["X-RateLimit-Remaining"]) == 2


# ── Bookings: user-scoped limiting ───────────────────────────────────


def _booking_payload(date_str="2099-01-01"):
    return {
        "chef_id": 1,
        "booking_date": date_str,
        "meal_slot": "DINNER",
        "special_requests": None,
    }


def test_bookings_limited_per_authenticated_user(limited_client):
    _signup(limited_client, "booklim@example.com")
    auth = _token_header(_login(limited_client, email="booklim@example.com"))

    first = limited_client.post("/api/bookings", json=_booking_payload(), headers=auth)
    second = limited_client.post("/api/bookings", json=_booking_payload(), headers=auth)
    third = limited_client.post("/api/bookings", json=_booking_payload(), headers=auth)

    assert first.status_code == 201
    assert second.status_code == 201
    assert third.status_code == 429
    assert third.headers["X-RateLimit-Limit"] == "2"


def test_chefs_endpoint_stays_usable_under_limiter(limited_client):
    for i in range(5):
        response = limited_client.get(
            "/api/chefs",
            headers={"X-Test-IP": f"10.1.{i}.1"},
        )
        assert response.status_code == 200
        assert len(response.json()["chefs"]) > 0


def test_chefs_endpoint_also_enforces_generous_limit(limited_client):
    for _ in range(5):
        assert limited_client.get("/api/chefs").status_code == 200
    sixth = limited_client.get("/api/chefs")
    assert sixth.status_code == 429


# ── Redis failure behavior ───────────────────────────────────────────


@pytest.fixture()
def broken_redis_client(monkeypatch):
    monkeypatch.setattr(settings, "RATE_LIMIT_ENABLED", True)

    def raise_redis_error(*_args, **_kwargs):
        raise RedisError("connection refused")

    monkeypatch.setattr(cache_redis, "_client", None)
    monkeypatch.setattr(cache_redis, "get_redis", raise_redis_error)
    monkeypatch.setattr(rate_limit_module, "get_redis", raise_redis_error)
    test_app, engine = _build_app()
    return TestClient(test_app), engine


def test_auth_fails_closed_when_redis_down(broken_redis_client):
    client, _engine = broken_redis_client
    response = client.post(
        "/api/auth/login",
        json={"email": "anyone@example.com", "password": "whatever123"},
    )
    assert response.status_code == 503
    assert response.json()["detail"] == "Rate limiter temporarily unavailable"


def test_chefs_fail_open_when_redis_down(broken_redis_client):
    client, _engine = broken_redis_client
    response = client.get("/api/chefs")
    assert response.status_code == 200


def test_bookings_fail_open_when_redis_down(broken_redis_client):
    from app.core.jwt import create_access_token

    client, engine = broken_redis_client

    session = Session(bind=engine)
    user = User(
        name="Outage User",
        email="outage@example.com",
        password_hash=hash_password("StrongPass123"),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    token = create_access_token(user.id)
    session.close()

    booking = client.post(
        "/api/bookings",
        json=_booking_payload(),
        headers={"Authorization": f"Bearer {token}"},
    )
    assert booking.status_code == 201


# ── Disabled limiter ─────────────────────────────────────────────────


def test_disabled_limiter_allows_unlimited_requests(monkeypatch):
    fake_client = FakeRedis(decode_responses=True)
    monkeypatch.setattr(cache_redis, "_client", fake_client)
    monkeypatch.setattr(settings, "RATE_LIMIT_ENABLED", False)
    test_app, _engine = _build_app()
    disabled = TestClient(test_app)

    for _ in range(10):
        assert _login(disabled).status_code in (200, 401)
    assert len(fake_client.keys("ratelimit:*")) == 0
