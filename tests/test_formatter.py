import unittest
from datetime import datetime, timezone

from arxiv_check.formatter import format_paper_list
from arxiv_check.models import Paper


class FormatterTests(unittest.TestCase):
    def test_numbered_paper_list_prefixes_titles_from_one(self):
        papers = [
            Paper(
                entry_id="first",
                title="First paper",
                link="https://example.com/first",
                summary="Summary",
                authors="A",
                published_at=datetime(2026, 3, 11, 8, 0, tzinfo=timezone.utc),
            ),
            Paper(
                entry_id="second",
                title="Second paper",
                link="https://example.com/second",
                summary="Summary",
                authors="B",
                published_at=datetime(2026, 3, 11, 9, 0, tzinfo=timezone.utc),
            ),
        ]

        message = format_paper_list(papers, numbered=True)

        self.assertIn("1. First paper", message)
        self.assertIn("2. Second paper", message)


if __name__ == "__main__":
    unittest.main()
