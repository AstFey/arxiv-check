import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from arxiv_check.config import AppConfig
from arxiv_check.models import AppState, Paper
from arxiv_check.service import check_for_new_papers


class ServiceTests(unittest.TestCase):
    @patch("arxiv_check.service.fetch_quant_ph_feed")
    def test_only_items_after_last_check_are_returned(self, mock_fetch):
        feed_items = [
            Paper(
                entry_id="old",
                title="Quantum cryptography overview",
                link="https://example.com/old",
                summary="Overview",
                authors="A",
                published_at=datetime(2026, 3, 10, 0, 0, tzinfo=timezone.utc),
            ),
            Paper(
                entry_id="new",
                title="Quantum cryptography protocol",
                link="https://example.com/new",
                summary="Protocol details",
                authors="B",
                published_at=datetime(2026, 3, 11, 8, 0, tzinfo=timezone.utc),
            ),
        ]
        mock_fetch.return_value = feed_items
        config = AppConfig(
            feed_url="https://rss.arxiv.org/rss/quant-ph",
            keywords=["quantum cryptography"],
            state_path=None,
            telegram_bot_token=None,
            telegram_chat_id=None,
            telegram_allowed_chat_ids=set(),
            feishu_webhook_url=None,
            feishu_webhook_secret=None,
        )
        state = AppState(
            last_checked_at=datetime(2026, 3, 11, 7, 0, tzinfo=timezone.utc),
            processed_item_ids=[],
            telegram_update_offset=0,
        )

        result, next_state = check_for_new_papers(
            config,
            state,
            now=datetime(2026, 3, 11, 9, 0, tzinfo=timezone.utc),
        )

        self.assertEqual([paper.entry_id for paper in result.papers], ["new"])
        self.assertEqual(next_state.last_checked_at, datetime(2026, 3, 11, 9, 0, tzinfo=timezone.utc))


if __name__ == "__main__":
    unittest.main()
