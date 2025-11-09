from __future__ import annotations

__all__ = ["convert_units"]

from .units_converter import UnitsConverter


def convert_units(
    *,
    label: str | None = None,
    value: int | float | None = None,
    units_from: str | None = None,
    units_to: str | None = None,
    places: int | None = None,
    mw: float | None = None,
) -> int | float:
    return UnitsConverter(
        label=label,
        value=value,
        units_from=units_from,
        units_to=units_to,
        places=places,
        mw=mw,
    ).converted_value
