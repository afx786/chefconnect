from datetime import datetime, timedelta, timezone

import jwt
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.api.routes.auth import router as auth_router
from app.core.config import settings
from app.core.jwt import create_access_token, decode_access_token
from app.core.security import hash_password, verify_password
from app.db.database import Base
from app.db.session import get_db
from app.models.user import User

app = FastAPI()
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])

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


def _override_get_db():
    db = Session(bind=_engine)
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db
client = TestClient(app)


# ── Password hashing ────────────────────────────────────────────────


def test_hash_password_returns_bcrypt_hash():
    h = hash_password("testpassword")
    assert h.startswith("$2")
    assert len(h) > 50


def test_verify_password_correct():
    h = hash_password("mypassword")
    assert verify_password("mypassword", h) is True


def test_verify_password_incorrect():
    h = hash_password("mypassword")
    assert verify_password("wrongpassword", h) is False


# ── JWT creation / verification ────────────────────────────────────


def test_create_access_token_returns_string():
    token = create_access_token(1)
    assert isinstance(token, str)
    assert len(token) > 20


def test_decode_access_token_valid():
    token = create_access_token(42)
    payload = decode_access_token(token)
    assert payload["sub"] == "42"
    assert "exp" in payload


def test_decode_access_token_contains_expiration():
    token = create_access_token(1)
    payload = decode_access_token(token)
    exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    assert exp > datetime.now(timezone.utc)


def test_decode_expired_token_rejected():
    from app.core.config import settings as _s

    expire = datetime.now(timezone.utc) - timedelta(minutes=1)
    payload = {"sub": "1", "exp": expire}
    token = jwt.encode(payload, _s.JWT_SECRET_KEY, algorithm=_s.JWT_ALGORITHM)
    try:
        decode_access_token(token)
        assert False, "Should have raised"
    except jwt.ExpiredSignatureError:
        pass


def test_decode_malformed_token_rejected():
    try:
        decode_access_token("not.a.valid.token")
        assert False, "Should have raised"
    except jwt.InvalidTokenError:
        pass


def test_decode_wrong_secret_rejected():
    token = jwt.encode(
        {"sub": "1", "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
        "wrong-secret",
        algorithm="HS256",
    )
    try:
        decode_access_token(token)
        assert False, "Should have raised"
    except jwt.InvalidSignatureError:
        pass


# ── Signup ──────────────────────────────────────────────────────────


def test_successful_signup():
    payload = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "securepass123",
    }
    resp = client.post("/api/auth/signup", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Test User"
    assert data["email"] == "test@example.com"
    assert "id" in data


def test_signup_response_no_password():
    payload = {
        "name": "No Password Leaked",
        "email": "noleak@example.com",
        "password": "securepass123",
    }
    resp = client.post("/api/auth/signup", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert "password" not in data
    assert "password_hash" not in data


def test_signup_duplicate_email_rejected():
    payload = {
        "name": "Duplicate User",
        "email": "dup@example.com",
        "password": "securepass123",
    }
    resp1 = client.post("/api/auth/signup", json=payload)
    assert resp1.status_code == 201

    payload2 = {
        "name": "Duplicate User 2",
        "email": "dup@example.com",
        "password": "anotherpass123",
    }
    resp2 = client.post("/api/auth/signup", json=payload2)
    assert resp2.status_code == 409


def test_signup_missing_required_fields():
    resp = client.post("/api/auth/signup", json={})
    assert resp.status_code == 422


def test_signup_invalid_email():
    payload = {
        "name": "Bad Email",
        "email": "not-an-email",
        "password": "securepass123",
    }
    resp = client.post("/api/auth/signup", json=payload)
    assert resp.status_code == 422


def test_signup_short_password():
    payload = {
        "name": "Short Pass",
        "email": "short@example.com",
        "password": "abc",
    }
    resp = client.post("/api/auth/signup", json=payload)
    assert resp.status_code == 422


def test_signup_stores_bcrypt_hash():
    payload = {
        "name": "Hash Check",
        "email": "hashcheck@example.com",
        "password": "securepass123",
    }
    resp = client.post("/api/auth/signup", json=payload)
    assert resp.status_code == 201

    db = Session(bind=_engine)
    user = db.query(User).filter(User.email == "hashcheck@example.com").first()
    assert user is not None
    assert user.password_hash.startswith("$2")
    assert user.password_hash != "securepass123"
    db.close()


def test_signup_normalizes_email():
    payload = {
        "name": "Normalized",
        "email": "  Normal@Example.COM  ",
        "password": "securepass123",
    }
    resp = client.post("/api/auth/signup", json=payload)
    assert resp.status_code == 201
    assert resp.json()["email"] == "normal@example.com"


def test_signup_trims_name():
    payload = {
        "name": "  Trimmed Name  ",
        "email": "trimmed@example.com",
        "password": "securepass123",
    }
    resp = client.post("/api/auth/signup", json=payload)
    assert resp.status_code == 201
    assert resp.json()["name"] == "Trimmed Name"


# ── Login ───────────────────────────────────────────────────────────


def _create_test_user(email: str = "login@example.com", password: str = "loginpass123"):
    db = Session(bind=_engine)
    user = db.query(User).filter(User.email == email).first()
    if user:
        db.close()
        return
    user = User(name="Login User", email=email, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    db.close()


def test_successful_login():
    _create_test_user()
    resp = client.post(
        "/api/auth/login",
        json={"email": "login@example.com", "password": "loginpass123"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_incorrect_password():
    _create_test_user()
    resp = client.post(
        "/api/auth/login",
        json={"email": "login@example.com", "password": "wrongpassword"},
    )
    assert resp.status_code == 401


def test_login_unknown_email():
    resp = client.post(
        "/api/auth/login",
        json={"email": "nonexistent@example.com", "password": "anypassword"},
    )
    assert resp.status_code == 401


def test_login_missing_fields():
    resp = client.post("/api/auth/login", json={})
    assert resp.status_code == 422


def test_login_returns_decodable_token():
    _create_test_user(email="tokentest@example.com", password="tokenpass123")
    resp = client.post(
        "/api/auth/login",
        json={"email": "tokentest@example.com", "password": "tokenpass123"},
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    payload = decode_access_token(token)
    assert payload["sub"] is not None
