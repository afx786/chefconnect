import json
from unittest.mock import patch

import fakeredis
from fastapi import FastAPI
from fastapi.testclient import TestClient
from redis import RedisError
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.api.routes.chefs import router as chefs_router
from app.core.config import settings
from app.db.database import Base
from app.db.session import get_db
from app.seed.seed_data import seed_database

fake_redis = fakeredis.FakeRedis(decode_responses=True)

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

_db_call_count = 0
_original_get_available_chefs = None


@event.listens_for(_engine, "before_cursor_execute")
def _count_db_calls(conn, cursor, statement, parameters, context, executemany):
    global _db_call_count
    _db_call_count += 1


def _override_get_db():
    db = Session(bind=_engine)
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db
client = TestClient(app)


def _patch_cache():
    return patch("app.cache.chef_cache.get_redis", return_value=fake_redis)


# ── Basic miss / hit ────────────────────────────────────────────────


def test_first_request_populates_cache():
    global _db_call_count
    _db_call_count = 0
    fake_redis.flushall()
    with _patch_cache():
        resp = client.get("/api/chefs")
    assert resp.status_code == 200
    keys = [k for k in fake_redis.keys() if k.startswith("cache:chefs:")]
    assert len(keys) >= 1
    assert _db_call_count >= 1


def test_second_identical_request_served_from_cache():
    global _db_call_count
    _db_call_count = 0
    fake_redis.flushall()
    with _patch_cache():
        first = client.get("/api/chefs")
        _db_call_count = 0
        second = client.get("/api/chefs")
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json() == second.json()
    assert _db_call_count == 0


# ── Filter-specific cache keys ──────────────────────────────────────


def test_different_cuisine_creates_different_key():
    fake_redis.flushall()
    with _patch_cache():
        client.get("/api/chefs?cuisine=Indian")
        client.get("/api/chefs?cuisine=Italian")
    keys = [k for k in fake_redis.keys() if k.startswith("cache:chefs:")]
    assert len(keys) >= 2
    indian = [k for k in keys if "Indian" in k]
    italian = [k for k in keys if "Italian" in k]
    assert len(indian) >= 1
    assert len(italian) >= 1


def test_different_locality_creates_different_key():
    fake_redis.flushall()
    with _patch_cache():
        client.get("/api/chefs?locality=Delhi")
        client.get("/api/chefs?locality=Noida")
    keys = [k for k in fake_redis.keys() if k.startswith("cache:chefs:")]
    assert len(keys) >= 2
    delhi = [k for k in keys if "Delhi" in k]
    noida = [k for k in keys if "Noida" in k]
    assert len(delhi) >= 1
    assert len(noida) >= 1


def test_cuisine_and_locality_combination_creates_own_key():
    fake_redis.flushall()
    with _patch_cache():
        client.get("/api/chefs?cuisine=Indian")
        client.get("/api/chefs?cuisine=Indian&locality=Delhi")
    keys = [k for k in fake_redis.keys() if k.startswith("cache:chefs:")]
    assert len(keys) >= 2


# ── Normalized filter equivalence ───────────────────────────────────


def test_equivalent_filters_use_same_key():
    fake_redis.flushall()
    global _db_call_count
    with _patch_cache():
        client.get("/api/chefs?cuisine=%20Indian%20")
        _db_call_count = 0
        client.get("/api/chefs?cuisine=Indian")
    assert _db_call_count == 0


# ── TTL ──────────────────────────────────────────────────────────────


def test_cache_ttl_is_set():
    fake_redis.flushall()
    with _patch_cache():
        client.get("/api/chefs")
    keys = [k for k in fake_redis.keys() if k.startswith("cache:chefs:")]
    assert len(keys) >= 1
    ttl = fake_redis.ttl(keys[0])
    assert ttl > 0
    assert ttl <= settings.CHEFS_CACHE_TTL_SECONDS


def test_expired_cache_causes_fresh_database_query():
    global _db_call_count
    fake_redis.flushall()
    with _patch_cache():
        client.get("/api/chefs")
        _db_call_count = 0
        keys = [k for k in fake_redis.keys() if k.startswith("cache:chefs:")]
        assert len(keys) >= 1
        fake_redis.expire(keys[0], 0)
        resp = client.get("/api/chefs")
    assert resp.status_code == 200
    assert _db_call_count >= 1


# ── Redis failure behavior ───────────────────────────────────────────


def test_redis_get_failure_still_returns_200():
    global _db_call_count
    _db_call_count = 0
    fake_redis.flushall()
    with patch("app.cache.chef_cache.get_redis") as mock:
        mock.return_value.get.side_effect = RedisError("connection lost")
        resp = client.get("/api/chefs")
    assert resp.status_code == 200
    assert _db_call_count >= 1
    data = resp.json()
    assert "chefs" in data
    assert isinstance(data["chefs"], list)


def test_redis_set_failure_still_returns_200():
    global _db_call_count
    _db_call_count = 0
    fake_redis.flushall()
    with patch("app.cache.chef_cache.get_redis") as mock:
        mock.return_value.get.return_value = None
        mock.return_value.setex.side_effect = RedisError("disk full")
        resp = client.get("/api/chefs")
    assert resp.status_code == 200
    assert _db_call_count >= 1


# ── Cached response shape ───────────────────────────────────────────


def test_cached_response_matches_database_shape():
    fake_redis.flushall()
    with _patch_cache():
        db_resp = client.get("/api/chefs")
        fake_redis.flushall()
        fresh_resp = client.get("/api/chefs")
    assert db_resp.status_code == 200
    assert fresh_resp.status_code == 200
    db_data = db_resp.json()
    fresh_data = fresh_resp.json()
    assert set(db_data.keys()) == set(fresh_data.keys())
    assert len(db_data["chefs"]) == len(fresh_data["chefs"])
    if db_data["chefs"]:
        assert set(db_data["chefs"][0].keys()) == set(fresh_data["chefs"][0].keys())


# ── No stale data across filters ────────────────────────────────────


def test_different_filter_values_do_not_share_entries():
    fake_redis.flushall()
    with _patch_cache():
        client.get("/api/chefs?cuisine=Indian")
        client.get("/api/chefs?cuisine=Italian")
    indian_keys = [k for k in fake_redis.keys() if "Indian" in k]
    italian_keys = [k for k in fake_redis.keys() if "Italian" in k]
    assert len(indian_keys) >= 1
    assert len(italian_keys) >= 1
    assert indian_keys != italian_keys


# ── Disabled TTL skips caching ──────────────────────────────────────


def test_zero_ttl_skips_caching():
    fake_redis.flushall()
    with _patch_cache(), patch.object(settings, "CHEFS_CACHE_TTL_SECONDS", 0):
        client.get("/api/chefs")
    keys = [k for k in fake_redis.keys() if k.startswith("cache:chefs:")]
    assert len(keys) == 0
