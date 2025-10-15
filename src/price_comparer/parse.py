from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import Optional, Tuple
from bs4 import BeautifulSoup


_CURRENCY_SYMBOLS = {
    "$": "USD",
    "€": "EUR",
    "£": "GBP",
    "¥": "JPY",
    "₹": "INR",
}


def _normalize_number_string(text: str) -> str:
    """Normalize a localized money string to a standard 1234.56 form.

    Heuristics:
    - If both comma and dot appear, the rightmost of them is decimal sep; remove the other.
    - If only comma appears and there is 1 comma with 1-2 digits after it, treat as decimal.
    - Otherwise remove commas and spaces and keep dot as decimal.
    """
    cleaned = text.strip()

    # Remove all but digits, separators, and minus
    cleaned = re.sub(r"[^0-9,.-]", "", cleaned)

    if not cleaned:
        return ""

    # Determine separators
    last_dot = cleaned.rfind(".")
    last_comma = cleaned.rfind(",")

    if last_dot != -1 and last_comma != -1:
        # Both present: assume the rightmost is decimal separator
        if last_dot > last_comma:
            # Dot is decimal, remove all commas
            number = cleaned.replace(",", "")
        else:
            # Comma is decimal, remove all dots then replace last comma with dot
            number = cleaned.replace(".", "")
            # Replace last comma with dot
            idx = number.rfind(",")
            number = number[:idx] + "." + number[idx + 1 :]
        return number

    if last_comma != -1 and last_dot == -1:
        # Only comma present
        parts = cleaned.split(",")
        if len(parts[-1]) in (1, 2):
            # Likely decimal comma
            return "".join(parts[:-1]).replace(",", "") + "." + parts[-1]
        # Otherwise treat commas as thousands
        return cleaned.replace(",", "")

    # Default: remove spaces and leave dot as decimal
    return cleaned.replace(" ", "")


def parse_price_text(text: str) -> Tuple[Optional[Decimal], Optional[str]]:
    """Extract a Decimal price and currency if present in text.

    Returns (price, currency), where currency is a symbol or ISO code if detected.
    """
    if not text:
        return None, None

    currency: Optional[str] = None

    # Capture common currency symbols or codes
    symbol_match = re.search(r"[\$€£¥₹]", text)
    code_match = re.search(r"\b(USD|EUR|GBP|JPY|INR)\b", text, re.IGNORECASE)

    if symbol_match:
        currency = symbol_match.group(0)
    elif code_match:
        currency = code_match.group(1).upper()

    normalized = _normalize_number_string(text)
    if not normalized:
        return None, currency

    try:
        value = Decimal(normalized)
        return value, currency
    except (InvalidOperation, ValueError):
        return None, currency


def extract_with_selectors(html: str, title_selector: str, price_selector: str) -> Tuple[str, Decimal, Optional[str]]:
    """Extract title and price from HTML with given CSS selectors.

    Raises ValueError if extraction fails.
    """
    soup = BeautifulSoup(html, "html.parser")

    title_el = soup.select_one(title_selector)
    price_el = soup.select_one(price_selector)

    if not title_el:
        raise ValueError(f"Title selector not found: {title_selector}")
    if not price_el:
        raise ValueError(f"Price selector not found: {price_selector}")

    title = title_el.get_text(strip=True)
    price_text = price_el.get_text(strip=True)

    price, currency = parse_price_text(price_text)
    if price is None:
        raise ValueError(f"Could not parse price from text: {price_text!r}")

    return title, price, currency
