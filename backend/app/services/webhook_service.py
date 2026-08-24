import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


def emit_booking_confirmed(*, booking_id: int, user_id: int, user_email: str,
                           user_name: str, chef_name: str, booking_date: str,
                           meal_slot: str) -> None:
    url = settings.N8N_BOOKING_CONFIRMED_WEBHOOK_URL
    if not url:
        return

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
        httpx.post(url, json=payload, timeout=10)
    except Exception:
        logger.warning("n8n webhook delivery failed for booking %d", booking_id)
