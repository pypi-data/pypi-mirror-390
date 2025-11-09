import math
from decimal import Decimal

from .round_half_up import round_half_up
from .round_up import round_up

__all__ = ["round_half_away_from_zero"]


def round_half_away_from_zero(n: float | Decimal, places: int | None = None):
    if isinstance(n, Decimal):
        places = Decimal("1" if not places else f"1.{str(0) * places}")
        return round_up(n, places=places)
    rounded_abs = round_half_up(abs(n), places)
    return math.copysign(rounded_abs, n)
