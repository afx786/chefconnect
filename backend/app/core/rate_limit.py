import time
from typing import Callable

from fastapi import HTTPException, Request, Response, status, Depends
from redis import RedisError

from app.cache.redis import get_redis
from app.api.deps import get_current_user
from app.core.config import settings
from app.models.user import User

KEY_PREFIX = "ratelimit"


def _scope_limit(scope: str) -> int:
    return {
        "auth": settings.RATE_LIMIT_AUTH_MAX_REQUESTS,
        "bookings": settings.RATE_LIMIT_BOOKINGS_MAX_REQUESTS,
        "chefs": settings.RATE_LIMIT_CHEFS_MAX_REQUESTS,
    }[scope]


def check_rate_limit(
    *,
    scope: str,
    identifier: str,
    limit: int,
) -> tuple[int, int]:
    """
    Fixed-window counter in Redis.

    Returns (remaining, retry_after_seconds).
    Raises RedisError so callers can apply their own failure policy.
    """
    client = get_redis()
    window = settings.RATE_LIMIT_WINDOW_SECONDS
    window_index = int(time.time()) // window
    key = f"{KEY_PREFIX}:{scope}:{identifier}:{window_index}"

    count = client.incr(key)
    if count == 1:
        client.expire(key, window)

    ttl = client.ttl(key)
    if ttl < 0:
        client.expire(key, window)
        ttl = window

    remaining = max(limit - count, 0)
    retry_after = max(ttl, 1) if count > limit else 0
    return remaining, retry_after


def _enforce(
    response: Response,
    *,
    scope: str,
    identifier: str,
) -> None:
    if not settings.RATE_LIMIT_ENABLED:
        return

    limit = _scope_limit(scope)
    try:
        remaining, retry_after = check_rate_limit(
            scope=scope,
            identifier=identifier,
            limit=limit,
        )
    except RedisError:
        raise

    window = settings.RATE_LIMIT_WINDOW_SECONDS
    reset_epoch = (int(time.time()) // window + 1) * window
    headers = {
        "X-RateLimit-Limit": str(limit),
        "X-RateLimit-Remaining": str(remaining),
        "X-RateLimit-Reset": str(reset_epoch),
    }

    if remaining == 0 and retry_after > 0:
        headers["Retry-After"] = str(retry_after)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests, please try again later",
            headers=headers,
        )

    for name, value in headers.items():
        response.headers[name] = value


def ip_rate_limit(scope: str, *, critical: bool = False) -> Callable:
    """
    IP-identified limiter for unauthenticated endpoints.

    critical=True (auth endpoints): Redis outage fails CLOSED with 503 so
    brute-force protection is never silently lost.
    critical=False: fail-open so a Redis outage cannot take browsing down.
    """

    def dependency(request: Request, response: Response) -> None:
        if not settings.RATE_LIMIT_ENABLED:
            return
        host = request.client.host if request.client else "unknown"
        try:
            _enforce(response, scope=scope, identifier=f"ip:{host}")
        except RedisError:
            if critical:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Rate limiter temporarily unavailable",
                )
            return

    return dependency


def user_rate_limit(scope: str) -> Callable:
    """
    Identity-scoped limiter for protected endpoints: the identifier comes
    from the JWT-authenticated user, falling back to client IP only if the
    identity dependency has not run yet.
    """

    def dependency(
        request: Request,
        response: Response,
        current_user: User = Depends(get_current_user),
    ) -> None:
        if not settings.RATE_LIMIT_ENABLED:
            return
        identifier = f"user:{current_user.id}"
        try:
            _enforce(response, scope=scope, identifier=identifier)
        except RedisError:
            return

    return dependency


ip_auth_limiter = ip_rate_limit("auth", critical=True)
ip_chefs_limiter = ip_rate_limit("chefs", critical=False)
booking_limiter = user_rate_limit("bookings")
