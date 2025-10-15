from decimal import Decimal
from pathlib import Path

from price_comparer.parse import parse_price_text, extract_with_selectors


def test_parse_price_text_various_formats():
    # USD with thousands and decimals
    value, currency = parse_price_text("$1,234.56")
    assert value == Decimal("1234.56")
    assert currency == "$"

    # Euro with comma decimal
    value, currency = parse_price_text("€999,99")
    assert value == Decimal("999.99")
    assert currency == "€"

    # Code + dot decimal
    value, currency = parse_price_text("USD 12.34")
    assert value == Decimal("12.34")
    assert currency == "USD"

    # German format with trailing symbol
    value, currency = parse_price_text("1.234,56 €")
    assert value == Decimal("1234.56")
    assert currency == "€"

    # Pounds without decimals
    value, currency = parse_price_text("£1,234")
    assert value == Decimal("1234")
    assert currency == "£"


def test_extract_with_selectors_from_fixture(tmp_path: Path):
    html = (Path(__file__).parent / "fixtures" / "shop_a.html").read_text(encoding="utf-8")
    title, price, currency = extract_with_selectors(html, "h1", ".price")
    assert title == "Widget A"
    assert price == Decimal("1234.56")
    assert currency == "$"
