from dataclasses import replace
from datetime import datetime, timezone
from typing import List, Tuple

from .arxiv import fetch_quant_ph_feed
from .config import AppConfig
from .filtering import match_keywords
from .models import AppState, CheckResult, Paper


def _is_new_since_last_check(paper: Paper, state: AppState) -> bool:
    if paper.entry_id in state.processed_item_ids:
        return False
    if state.last_checked_at is None:
        return True
    if paper.published_at is None:
        return False
    return paper.published_at > state.last_checked_at


def check_for_new_papers(
    config: AppConfig,
    state: AppState,
    now: datetime = None,
) -> Tuple[CheckResult, AppState]:
    checked_at = now or datetime.now(timezone.utc)
    feed_items = fetch_quant_ph_feed(config.feed_url)

    matched_papers: List[Paper] = []
    processed_ids = list(state.processed_item_ids)

    for paper in feed_items:
        if not _is_new_since_last_check(paper, state):
            continue
        processed_ids.append(paper.entry_id)
        matched_keywords = match_keywords(paper, config.keywords)
        if not matched_keywords:
            continue
        matched_papers.append(replace(paper, matched_keywords=matched_keywords))

    next_state = AppState(
        last_checked_at=checked_at,
        processed_item_ids=processed_ids,
        telegram_update_offset=state.telegram_update_offset,
    )
    return (
        CheckResult(
            checked_at=checked_at,
            papers=matched_papers,
            matched_count=len(matched_papers),
            fetched_count=len(feed_items),
        ),
        next_state,
    )

