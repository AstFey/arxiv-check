import unittest
from datetime import datetime, timezone

from arxiv_check.filtering import match_keywords
from arxiv_check.models import Paper


class FilteringTests(unittest.TestCase):
    def test_match_keywords_uses_plain_substring_matching(self):
        paper = Paper(
            entry_id="1",
            title="Fault-Tolerant Quantum Computing with Surface Codes",
            link="https://example.com/1",
            summary="We study quantum error correction in detail.",
            authors="A. Author",
            published_at=datetime(2026, 3, 11, tzinfo=timezone.utc),
        )

        matches = match_keywords(paper, ["surface code", "magic state", "error correction"])

        self.assertEqual(matches, ["surface code", "error correction"])


if __name__ == "__main__":
    unittest.main()

