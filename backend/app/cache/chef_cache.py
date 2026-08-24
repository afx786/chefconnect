import json
from urllib.parse import quote

from redis import RedisError

from app.cache.redis import get_redis
from app.core.config import settings
from app.schemas.chef import ChefListResponse
from app.services.chef_service import normalize_filter

KEY_PREFIX = "cache:chefs"


def _build_key(cuisine: str | None, locality: str | None) -> str:
    cuisine = normalize_filter(cuisine)
    locality = normalize_filter(locality)
    parts: list[str] = []
    if cuisine:
        parts.append(f"cuisine={quote(cuisine, safe='')}")
    if locality:
        parts.append(f"locality={quote(locality, safe='')}")
    suffix = "&".join(parts) if parts else "all"
    return f"{KEY_PREFIX}:{suffix}"


def get_cached_chefs(cuisine: str | None, locality: str | None) -> ChefListResponse | None:
    try:
        cached = get_redis().get(_build_key(cuisine, locality))
        if cached is not None:
            return ChefListResponse.model_validate_json(cached)
    except RedisError:
        pass
    return None


def set_cached_chefs(
    cuisine: str | None,
    locality: str | None,
    response: ChefListResponse,
) -> None:
    try:
        ttl = settings.CHEFS_CACHE_TTL_SECONDS
        if ttl > 0:
            get_redis().set(
                _build_key(cuisine, locality),
                response.model_dump_json(),
                ex=ttl,
            )
    except RedisError:
        pass
