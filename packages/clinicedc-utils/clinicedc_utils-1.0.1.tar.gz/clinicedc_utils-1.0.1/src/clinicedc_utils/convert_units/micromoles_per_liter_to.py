from clinicedc_constants import (
    GRAMS_PER_LITER,
    MICROMOLES_PER_LITER,
    MILLIGRAMS_PER_DECILITER,
    MILLIMOLES_PER_LITER,
)

from ..exceptions import ConversionNotHandled

__all__ = ["micromoles_per_liter_to"]


def micromoles_per_liter_to(
    *, value: float | int, units_to: str, mw: float | None = None
) -> dict:
    if units_to == MICROMOLES_PER_LITER:
        return {MICROMOLES_PER_LITER: float(value)}
    if units_to == MILLIMOLES_PER_LITER:
        return {MILLIMOLES_PER_LITER: float(value) / 1000.00}
    if units_to == GRAMS_PER_LITER:
        if mw is None:
            raise ConversionNotHandled("Molecular weight may not be None.")
        return {GRAMS_PER_LITER: (float(value) * mw) / 100.00}
    if units_to == MILLIGRAMS_PER_DECILITER:
        if mw is None:
            raise ConversionNotHandled("Molecular weight may not be None.")
        return {MILLIGRAMS_PER_DECILITER: (float(value) * mw) / 10000.00}
    raise ConversionNotHandled(f"Conversion not found. Tried umol/L to {units_to}. ")
