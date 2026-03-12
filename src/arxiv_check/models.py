from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass(frozen=True)
class Paper:
    entry_id: str
    title: str
    link: str
    summary: str
    authors: str
    published_at: Optional[datetime]
    matched_keywords: List[str] = field(default_factory=list)


@dataclass
class AppState:
    last_checked_at: Optional[datetime] = None
    processed_item_ids: List[str] = field(default_factory=list)
    telegram_update_offset: int = 0


@dataclass(frozen=True)
class CheckResult:
    checked_at: datetime
    papers: List[Paper]
    matched_count: int
    fetched_count: int

