import logging
from urllib.parse import urlparse

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


def emit_booking_confirmed(*, booking_id: int, user_id: int, user_email: str,
                           user_name: str, chef_name: str, booking_date: str,
                           meal_slot: str) -> None:
    url = settings.N8N_BOOKING_CONFIRMED_WEBHOOK_URL
    if not url:
        logger.warning("WEBHOOK_ATTEMPT booking=%d url=<EMPTY> — skipping", booking_id)
        return

    parsed = urlparse(url)
    logger.info(
        "WEBHOOK_ATTEMPT booking=%d host=%s path=%s",
        booking_id, parsed.hostname, parsed.path,
    )

    payload = {
        "event": "booking.confirmed",
        "event_id": f"booking_confirmed_{booking_id}",
        "booking_id": booking_id,
        "user_id": user_id,
        "user_email": user_email,
        "user_name": user_name,
        "chef_name": chef_name,
        "booking_date": booking_date,
        "meal_slot": meal_slot,
        "status": "CONFIRMED",
    }

    try:
        resp = httpx.post(url, json=payload, timeout=10)
        logger.info(
            "WEBHOOK_RESPONSE booking=%d status=%d", booking_id, resp.status_code,
        )
    except Exception as exc:
        logger.warning(
            "WEBHOOK_ERROR booking=%d type=%s msg=%s",
            booking_id, type(exc).__name__, exc,
        )
