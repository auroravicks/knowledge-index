from __future__ import annotations

import json
import logging
from typing import Any
from urllib.request import Request, urlopen

from .config import Config

LOGGER = logging.getLogger(__name__)


def build_index_summary(result: dict[str, Any], max_items: int = 20) -> str:
    lines = [
        "🧠 *Knowledge index complete*",
        "",
        f"• Total searchable documents: {result['files']}",
        f"• Added: {len(result['added'])}",
        f"• Updated: {len(result['updated'])}",
        f"• Removed: {len(result['removed'])}",
        f"• Unchanged: {result['unchanged']}",
        f"• Extraction errors: {len(result['errors'])}",
    ]
    remaining = max_items
    for heading, key in (("New documents", "added"), ("Updated documents", "updated"), ("Removed documents", "removed")):
        values = result[key]
        if not values or remaining <= 0:
            continue
        shown = values[:remaining]
        lines.extend(["", f"*{heading}*"])
        lines.extend(f"• {value}" for value in shown)
        remaining -= len(shown)
    hidden = len(result["added"]) + len(result["updated"]) + len(result["removed"]) - max_items
    if hidden > 0:
        lines.append(f"• …and {hidden} more")
    if result["errors"]:
        lines.extend(["", "*Extraction errors*"])
        lines.extend(f"• {value}" for value in result["errors"][:5])
    return "\n".join(lines)


def send_index_summary(config: Config, result: dict[str, Any]) -> None:
    if not config.google_chat_enabled:
        LOGGER.info("Google Chat notifications are disabled")
        return
    if not config.google_chat_webhook_url:
        raise ValueError("GOOGLE_CHAT_WEBHOOK_URL is not configured in Knowledge/.env")
    payload = json.dumps({"text": build_index_summary(result, config.summary_max_items)}).encode("utf-8")
    request = Request(
        config.google_chat_webhook_url,
        data=payload,
        headers={"Content-Type": "application/json; charset=UTF-8"},
        method="POST",
    )
    with urlopen(request, timeout=30) as response:
        if not 200 <= response.status < 300:
            raise RuntimeError(f"Google Chat returned HTTP {response.status}")
    LOGGER.info("Google Chat knowledge summary delivered")
