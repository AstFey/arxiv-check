import base64
import hashlib
import hmac
import json
import time
from datetime import timezone, timedelta
from typing import Optional
from urllib.request import Request, urlopen

from .formatter import format_paper_list
from .models import CheckResult
from .ssl_utils import build_ssl_context


class FeishuError(RuntimeError):
    pass


def _make_sign(secret: str, timestamp: int) -> str:
    """Generate HMAC-SHA256 signature required by Feishu signed webhooks."""
    string_to_sign = f"{timestamp}\n{secret}"
    sig = hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()
    return base64.b64encode(sig).decode("utf-8")


def _post_json(url: str, payload: dict) -> dict:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = Request(url, data=data, headers={"Content-Type": "application/json; charset=utf-8"})
    with urlopen(request, timeout=60, context=build_ssl_context()) as response:
        result = json.loads(response.read().decode("utf-8"))
    if result.get("code", 0) != 0:
        raise FeishuError(f"Feishu API error: {result}")
    return result


def send_text(webhook_url: str, text: str, secret: Optional[str] = None) -> None:
    """Send a plain-text message to a Feishu incoming webhook."""
    payload: dict = {"msg_type": "text", "content": {"text": text}}
    if secret:
        timestamp = int(time.time())
        payload["timestamp"] = str(timestamp)
        payload["sign"] = _make_sign(secret, timestamp)
    _post_json(webhook_url, payload)


_CST = timezone(timedelta(hours=8))


def send_check_result(webhook_url: str, result: CheckResult, secret: Optional[str] = None) -> None:
    checked_at_cst = result.checked_at.astimezone(_CST)
    checked_at_str = checked_at_cst.strftime("%Y-%m-%d %H:%M:%S CST")
    summary = f"检查了 {result.fetched_count} 条 feed，检查时间：{checked_at_str}\n\n"
    message = summary + format_paper_list(result.papers)
    _send_chunked(webhook_url, message, secret)


def _send_chunked(webhook_url: str, text: str, secret: Optional[str], limit: int = 4000) -> None:
    chunks: list = []
    current: list = []
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
        send_text(webhook_url, chunk, secret)
        time.sleep(0.3)
