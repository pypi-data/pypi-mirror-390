from clinicedc_constants import (
    GRAMS_PER_LITER,
    MICROMOLES_PER_LITER,
    MILLIGRAMS_PER_DECILITER,
    MILLIMOLES_PER_LITER,
)

from ..constants import molecular_weights
from ..exceptions import ConversionNotHandled
from ..round_up import round_half_away_from_zero
from .micromoles_per_liter_to import micromoles_per_liter_to
from .milligrams_per_deciliter_to import milligrams_per_deciliter_to

__all__ = ["UnitsConverter"]


class UnitsConverter:
    def __init__(
        self,
        *,
        label: str,
        value: int | float,
        units_from: str,
        units_to: str,
        places: int | None = None,
        mw: float | None = None,
    ):
        self.label = label
        self.value = value
        self.units_from = units_from
        self.units_to = units_to
        self.places = places or 4
        self._mw = mw
        if label is None:
            raise ValueError("label is required. See convert_units.")
        if value is not None and units_from and units_to and units_from != units_to:
            self.converted_value = self.get_converted_value()
        elif units_from == units_to:
            self.converted_value = value
        else:
            raise ConversionNotHandled(
                f"Conversion not handled. Tried {label} from {units_from} to {units_to}."
            )

    @property
    def mw(self) -> float | int:
        if self._mw is None:
            try:
                self._mw = molecular_weights[self.label]
            except KeyError as e:
                raise ConversionNotHandled(
                    f"Molecular weight may not be None. Got {self.label}."
                ) from e
        return self._mw

    def round_up(self, converted_value):
        try:
            converted_value = round_half_away_from_zero(converted_value, self.places)
        except TypeError as e:
            raise ConversionNotHandled(
                f"Conversion not handled. Tried {self.label} from {self.units_from} "
                f"to {self.units_to}. "
                f"Got {e} when rounding {converted_value} to {self.places} places."
            ) from e
        return converted_value

    def from_milligrams_per_deciliter(self) -> float | int:
        if self.units_to != MILLIGRAMS_PER_DECILITER:
            return milligrams_per_deciliter_to(
                value=float(self.value), units_to=self.units_to, mw=self.mw
            )[self.units_to]
        return self.value

    def from_grams_per_liter(self) -> float | int:
        if self.units_to != GRAMS_PER_LITER:
            return milligrams_per_deciliter_to(
                value=float(self.value) * 100.00,
                units_to=self.units_to,
                mw=self.mw,
            )[self.units_to]
        return self.value

    def from_millimoles_per_liter(self) -> float | int:
        if self.units_to != MILLIMOLES_PER_LITER:
            return micromoles_per_liter_to(
                value=self.value / 1000, units_to=self.units_to, mw=self.mw
            )[self.units_to]
        return self.value

    def from_micromoles_per_liter(self):
        if self.units_to != MICROMOLES_PER_LITER:
            return micromoles_per_liter_to(
                value=self.value, units_to=self.units_to, mw=self.mw
            )[self.units_to]
        return self.value

    def get_converted_value(self) -> int | float:
        converted_value = None
        if self.units_from == MILLIGRAMS_PER_DECILITER:
            converted_value = self.from_milligrams_per_deciliter()
        elif self.units_from == GRAMS_PER_LITER:
            converted_value = self.from_grams_per_liter()
        elif self.units_from == MILLIMOLES_PER_LITER:
            converted_value = self.from_millimoles_per_liter()
        elif self.units_from == MICROMOLES_PER_LITER:
            converted_value = self.from_micromoles_per_liter()
        if not converted_value:
            raise ConversionNotHandled(
                f"Conversion not handled. Tried {self.label} from "
                f"{self.units_from} to {self.units_to}."
            )
        return self.round_up(converted_value)
