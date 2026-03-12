import json
import time
from typing import Iterable, List
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .formatter import format_paper_list
from .models import CheckResult
from .ssl_utils import build_ssl_context


class TelegramError(RuntimeError):
    pass


def _telegram_api(token: str, method: str) -> str:
    return f"https://api.telegram.org/bot{token}/{method}"


def _request_json(url: str, data=None):
    request = Request(url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urlopen(request, timeout=60, context=build_ssl_context()) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not payload.get("ok"):
        raise TelegramError(str(payload))
    return payload["result"]


def send_message(token: str, chat_id: str, text: str) -> None:
    payload = urlencode({"chat_id": chat_id, "text": text}).encode("utf-8")
    _request_json(_telegram_api(token, "sendMessage"), payload)


def get_me(token: str) -> dict:
    return _request_json(_telegram_api(token, "getMe"))


def send_check_result(token: str, chat_id: str, result: CheckResult) -> None:
    summary = f"Checked {result.fetched_count} feed items at {result.checked_at.isoformat()}.\n\n"
    message = summary + format_paper_list(result.papers)
    _send_chunked_message(token, chat_id, message)


def _send_chunked_message(token: str, chat_id: str, text: str, limit: int = 3500) -> None:
    chunks = []
    current = []
    current_length = 0

    for section in text.split("\n\n"):
        section_length = len(section) + 2
        if current and current_length + section_length > limit:
            chunks.append("\n\n".join(current))
            current = [section]
            current_length = section_length
        else:
            current.append(section)
            current_length += section_length

    if current:
        chunks.append("\n\n".join(current))

    for chunk in chunks:
        send_message(token, chat_id, chunk)
        time.sleep(0.3)


def get_updates(token: str, offset: int) -> List[dict]:
    query = urlencode({"timeout": 30, "offset": offset + 1})
    return _request_json(f"{_telegram_api(token, 'getUpdates')}?{query}")


def extract_chat_id(update: dict) -> str:
    message = update.get("message") or {}
    chat = message.get("chat") or {}
    return str(chat.get("id", ""))


def extract_text(update: dict) -> str:
    message = update.get("message") or {}
    return str(message.get("text", "")).strip()


def newest_offset(updates: Iterable[dict], current_offset: int) -> int:
    offset = current_offset
    for update in updates:
        offset = max(offset, int(update.get("update_id", 0)))
    return offset
