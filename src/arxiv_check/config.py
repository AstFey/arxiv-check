import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Set


DEFAULT_KEYWORDS = [
    "quantum computing",
    "quantum computation",
    "quantum complexity",
    "query complexity",
    "communication complexity",
    "quantum cryptography",
    "quantum key distribution",
    "qkd",
    "quantum error correction",
    "fault tolerance",
    "fault-tolerant",
    "quantum code",
    "stabilizer code",
    "surface code",
    "magic state",
    "logical qubit",
    "bosonic code",
]


@dataclass(frozen=True)
class AppConfig:
    feed_url: str
    keywords: List[str]
    state_path: Path
    telegram_bot_token: Optional[str]
    telegram_chat_id: Optional[str]
    telegram_allowed_chat_ids: Set[str]


def _split_csv(value: Optional[str]) -> List[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def load_config() -> AppConfig:
    keyword_values = _split_csv(os.getenv("ARXIV_KEYWORDS"))
    return AppConfig(
        feed_url=os.getenv("ARXIV_FEED_URL", "https://rss.arxiv.org/rss/quant-ph"),
        keywords=keyword_values or DEFAULT_KEYWORDS,
        state_path=Path(os.getenv("ARXIV_STATE_PATH", ".data/state.json")),
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
        telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID"),
        telegram_allowed_chat_ids=set(_split_csv(os.getenv("TELEGRAM_ALLOWED_CHAT_IDS"))),
    )

