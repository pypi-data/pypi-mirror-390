from __future__ import annotations

import decimal
from decimal import Decimal

__all__ = ["round_up"]


def round_up(value: Decimal, places: Decimal | None = None):
    places = places or Decimal("1.0000")
    if value > Decimal("0.0000000000"):
        decimal.getcontext().rounding = decimal.ROUND_HALF_UP
    else:
        decimal.getcontext().rounding = decimal.ROUND_HALF_DOWN
    return value.quantize(places)
