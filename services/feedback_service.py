"""Feedback service — persist 👍/👎 ratings to data/feedback.json."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from config.settings import get_settings
from utils.file_utils import read_json, write_json


def record_feedback(message_id: str, rating: str, comment: str = "") -> None:
    """Append a feedback entry. Idempotent per (message_id, rating)."""
    path = Path(get_settings().FEEDBACK_PATH)
    entries = read_json(path, default=[])
    # If already rated with same direction, skip.
    for e in entries:
        if e.get("message_id") == message_id and e.get("rating") == rating:
            return
    entries.append(
        {
            "message_id": message_id,
            "rating": rating,
            "comment": comment,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )
    write_json(path, entries)