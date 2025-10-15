from __future__ import annotations

import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import List, Dict, Any

import click
from rich.console import Console
from rich.table import Table

from .fetch import fetch_url
from .parse import extract_with_selectors
from .models import ProductPrice
from .compare import sort_by_price


console = Console()


def _format_price(value: Decimal, currency: str | None) -> str:
    quantized = value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if currency in {"$", "€", "£", "¥", "₹"}:
        return f"{currency}{quantized}"
    if currency in {"USD", "EUR", "GBP", "JPY", "INR"}:
        symbol = {"USD": "$", "EUR": "€", "GBP": "£", "JPY": "¥", "INR": "₹"}[currency]
        return f"{symbol}{quantized}"
    return f"{quantized}"


@click.command()
@click.option(
    "--config",
    "config_path",
    type=click.Path(exists=True, dir_okay=False, readable=True, path_type=Path),
    required=True,
    help="Path to JSON config with sources.",
)
@click.option("--json-output", is_flag=True, help="Output JSON instead of a table")
@click.option("--timeout", type=float, default=15.0, show_default=True, help="Request timeout seconds")
def main(config_path: Path, json_output: bool, timeout: float) -> None:
    """Compare product prices across websites defined in a JSON config.

    Config format:
    {
      "sources": [
        {
          "name": "Shop A",
          "url": "https://example.com/product/123",
          "title_selector": "h1",
          "price_selector": ".price"
        }
      ]
    }
    """
    data = json.loads(config_path.read_text(encoding="utf-8"))
    sources: List[Dict[str, Any]] = data.get("sources", [])
    if not sources:
        raise click.ClickException("No sources defined in config")

    results: List[ProductPrice] = []
    for src in sources:
        name = src.get("name") or src.get("id") or src.get("url")
        url = src["url"]
        title_sel = src.get("title_selector") or "title"
        price_sel = src["price_selector"]

        try:
            html = fetch_url(url, timeout=timeout)
            title, price, currency = extract_with_selectors(html, title_sel, price_sel)
            results.append(
                ProductPrice(source=str(name), title=title, url=url, price=price, currency=currency)
            )
        except Exception as exc:  # noqa: BLE001 - surface errors to user
            raise click.ClickException(f"Failed for {name} ({url}): {exc}") from exc

    results = sort_by_price(results)

    if json_output:
        # Convert Decimals to strings for JSON compatibility
        payload = []
        for r in results:
            item = r.model_dump()
            price_value = item.get("price")
            if isinstance(price_value, Decimal):
                item["price"] = str(price_value)
            payload.append(item)
        console.print_json(data=payload)
        return

    table = Table(title="Price Comparison", show_header=True, header_style="bold")
    table.add_column("Source", style="cyan", no_wrap=True)
    table.add_column("Title", style="white")
    table.add_column("Price", style="green", justify="right")
    table.add_column("URL", style="magenta")

    for r in results:
        table.add_row(r.source, r.title, _format_price(r.price, r.currency), r.url)

    console.print(table)
