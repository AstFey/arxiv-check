import json
from datetime import datetime
from pathlib import Path

from .models import AppState


MAX_PROCESSED_IDS = 2000


def _parse_datetime(value):
    if not value:
        return None
    return datetime.fromisoformat(value)


def load_state(path: Path) -> AppState:
    if not path.exists():
        return AppState()

    data = json.loads(path.read_text(encoding="utf-8"))
    return AppState(
        last_checked_at=_parse_datetime(data.get("last_checked_at")),
        processed_item_ids=list(data.get("processed_item_ids", [])),
        telegram_update_offset=int(data.get("telegram_update_offset", 0)),
    )


def save_state(path: Path, state: AppState) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    processed_ids = state.processed_item_ids[-MAX_PROCESSED_IDS:]
    data = {
        "last_checked_at": state.last_checked_at.isoformat() if state.last_checked_at else None,
        "processed_item_ids": processed_ids,
        "telegram_update_offset": state.telegram_update_offset,
    }
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")

