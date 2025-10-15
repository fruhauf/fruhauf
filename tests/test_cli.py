import json
from decimal import Decimal
from pathlib import Path

from click.testing import CliRunner

from price_comparer.cli import main


def test_cli_json_output(tmp_path: Path):
    fixtures = Path(__file__).parent / "fixtures"
    cfg = {
        "sources": [
            {
                "name": "Shop A",
                "url": f"file://{(fixtures / 'shop_a.html').resolve()}",
                "title_selector": "h1",
                "price_selector": ".price",
            },
            {
                "name": "Shop B",
                "url": f"file://{(fixtures / 'shop_b.html').resolve()}",
                "title_selector": "h1",
                "price_selector": ".price",
            },
        ]
    }
    cfg_path = tmp_path / "config.json"
    cfg_path.write_text(json.dumps(cfg), encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(main, ["--config", str(cfg_path), "--json-output"]) 
    assert result.exit_code == 0, result.output

    data = json.loads(result.output)
    assert len(data) == 2

    assert data[0]["source"] == "Shop B"  # cheaper first
    assert Decimal(str(data[0]["price"])) == Decimal("999.99")
    assert data[0]["currency"] in ("€", "EUR")

    assert data[1]["source"] == "Shop A"
    assert Decimal(str(data[1]["price"])) == Decimal("1234.56")
    assert data[1]["currency"] in ("$", "USD")
