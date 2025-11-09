from clinicedc_constants import (
    GRAMS_PER_LITER,
    MICROMOLES_PER_LITER,
    MILLIGRAMS_PER_DECILITER,
    MILLIGRAMS_PER_LITER,
    MILLIMOLES_PER_LITER,
)

from ..exceptions import ConversionNotHandled

__all__ = ["milligrams_per_deciliter_to"]


def milligrams_per_deciliter_to(
    *, value: float | int, units_to: str, mw: float | None = None
) -> dict[str, float]:
    if units_to == MILLIGRAMS_PER_DECILITER:
        return {MILLIGRAMS_PER_DECILITER: float(value)}
    if units_to == MILLIMOLES_PER_LITER:
        if mw is None:
            raise ConversionNotHandled("Molecular weight may not be None.")
        return {MILLIMOLES_PER_LITER: (float(value) * 10.00) / mw}
    if units_to == MICROMOLES_PER_LITER:
        if mw is None:
            raise ConversionNotHandled("Molecular weight may not be None.")
        return {MICROMOLES_PER_LITER: (float(value) * 10000.00) / mw}
    if units_to == MILLIGRAMS_PER_LITER:
        return {MILLIGRAMS_PER_LITER: float(value) * 10.00}
    if units_to == GRAMS_PER_LITER:
        return {GRAMS_PER_LITER: float(value) / 100.00}
    raise ConversionNotHandled(f"Conversion not found. Tried mg/dL to {units_to}. ")
