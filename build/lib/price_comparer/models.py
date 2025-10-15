from __future__ import annotations

from decimal import Decimal
from typing import Optional
from pydantic import BaseModel


class ProductPrice(BaseModel):
    source: str
    title: str
    url: str
    price: Decimal
    currency: Optional[str] = None

    class Config:
        frozen = True
