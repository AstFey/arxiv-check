from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import List
from urllib.error import URLError
from urllib.request import Request, urlopen
from xml.etree import ElementTree

from .models import Paper
from .ssl_utils import build_ssl_context


def _get_child_text(node, tag_name, default=""):
    child = node.find(tag_name)
    if child is None or child.text is None:
        return default
    return child.text.strip()


def _parse_pub_date(value: str):
    if not value:
        return None
    parsed = parsedate_to_datetime(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def fetch_quant_ph_feed(feed_url: str) -> List[Paper]:
    request = Request(
        feed_url,
        headers={"User-Agent": "arxiv-check/0.1 (+https://arxiv.org)"},
    )
    try:
        with urlopen(request, timeout=30, context=build_ssl_context()) as response:
            payload = response.read()
    except URLError as exc:
        raise RuntimeError(f"Failed to fetch RSS feed from {feed_url}: {exc}") from exc

    root = ElementTree.fromstring(payload)
    channel = root.find("channel")
    if channel is None:
        return []

    papers = []
    for item in channel.findall("item"):
        link = _get_child_text(item, "link")
        guid = _get_child_text(item, "guid", default=link)
        papers.append(
            Paper(
                entry_id=guid or link,
                title=_get_child_text(item, "title"),
                link=link,
                summary=_get_child_text(item, "description"),
                authors=_get_child_text(item, "{http://purl.org/dc/elements/1.1/}creator"),
                published_at=_parse_pub_date(_get_child_text(item, "pubDate")),
            )
        )

    return sorted(
        papers,
        key=lambda paper: paper.published_at or datetime.min.replace(tzinfo=timezone.utc),
    )
