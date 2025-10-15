from __future__ import annotations

from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ProductPrice(BaseModel):
    source: str
    title: str
    url: str
    price: Decimal
    currency: Optional[str] = None

    # Pydantic v2 model configuration
    model_config = ConfigDict(frozen=True)
