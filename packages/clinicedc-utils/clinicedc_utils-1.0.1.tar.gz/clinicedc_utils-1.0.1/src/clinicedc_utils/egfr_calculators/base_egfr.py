from __future__ import annotations

from clinicedc_constants import FEMALE, MALE, MICROMOLES_PER_LITER, MILLIGRAMS_PER_DECILITER

from clinicedc_utils.constants import molecular_weights

from ..exceptions import EgfrCalculatorError

__all__ = ["BaseEgfr"]


class BaseEgfr:
    male = MALE
    female = FEMALE
    micromoles_per_liter = MICROMOLES_PER_LITER
    milligrams_per_deciliter = MILLIGRAMS_PER_DECILITER
    min_age_in_years = 18.0
    max_age_in_years = 120.0
    mw_creatinine = molecular_weights["creatinine"]  # g/mol
    allowed_units = (MICROMOLES_PER_LITER, MILLIGRAMS_PER_DECILITER)

    def __init__(
        self,
        *,
        gender: str | None = None,
        age_in_years: int | float | None = None,
        creatinine_value: float | int | None = None,
        creatinine_units: str | None = None,
    ):
        self.creatinine_value = creatinine_value
        self.creatinine_units = creatinine_units

        if self.creatinine_units not in self.allowed_units:
            raise EgfrCalculatorError(
                f"Invalid creatinine units. Expected one of {self.allowed_units}. "
                f"Got {creatinine_units}"
            )

        if not gender or gender not in [self.male, self.female]:
            raise EgfrCalculatorError(
                f"Invalid gender. Expected one of {self.male}, {self.female}. Got {gender}."
            )
        self.gender = gender

        if not (self.min_age_in_years <= (age_in_years or 0.0) < self.max_age_in_years):
            raise EgfrCalculatorError(
                f"Invalid age. See {self.__class__.__name__}. Got {age_in_years}"
            )
        self.age_in_years = float(age_in_years) if age_in_years else None
