from __future__ import annotations

from typing import Iterable, List
from .models import ProductPrice


def sort_by_price(prices: Iterable[ProductPrice]) -> List[ProductPrice]:
    """Return a new list sorted by ascending price."""
    return sorted(prices, key=lambda p: (p.price, p.source))
