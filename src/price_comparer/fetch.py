from __future__ import annotations

from pathlib import Path
from typing import Final
import httpx

DEFAULT_HEADERS: Final = {
    "User-Agent": (
        "price-comparer/0.1 (+https://example.invalid; support@example.invalid) "
        "Python-HTTPX"
    )
}


def fetch_url(url: str, timeout: float = 15.0) -> str:
    """Fetch URL content and return text body.

    Supports local files with file:// URLs for testing.
    """
    if url.startswith("file://"):
        file_path = url[len("file://") :]
        return Path(file_path).read_text(encoding="utf-8")

    with httpx.Client(headers=DEFAULT_HEADERS, timeout=timeout, follow_redirects=True) as client:
        response = client.get(url)
        response.raise_for_status()
        return response.text
