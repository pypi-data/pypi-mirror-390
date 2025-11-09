from __future__ import annotations

from decimal import Decimal

from clinicedc_utils import convert_units

from .base_egfr import BaseEgfr, EgfrCalculatorError

__all__ = ["EgfrCockcroftGault"]


class EgfrCockcroftGault(BaseEgfr):
    """Reference https://www.mdcalc.com/creatinine-clearance-cockcroft-gault-equation

    Cockcroft-Gault

    eGFR (mL/min) = { (140 – age (years)) x weight (kg) x constant*} /
    serum creatinine (μmol/L)
    *constant = 1.23 for males and 1.05 for females

    Cockcroft-Gault CrCl, mL/min =
        (140 – age) × (weight, kg) × (0.85 if female) / (72 × SCr(mg/dL))

    or:

    https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2763564/

    GFR = 141 × min(Scr/κ, 1)α × max(Scr/κ, 1)-1.209 × 0.993Age
    """  # noqa: RUF002

    def __init__(self, weight: int | float | Decimal | None = None, **kwargs):
        super().__init__(**kwargs)
        self.weight = float(weight) if weight else None
        if self.creatinine_units == self.milligrams_per_deciliter:
            self.creatinine_value = convert_units(
                label="creatinine",
                value=float(self.creatinine_value),
                units_from=self.creatinine_units,
                units_to=self.micromoles_per_liter,
                mw=self.mw_creatinine,
            )

    @property
    def value(self) -> float:
        """Returns the eGFR value or raises.

        eGFR (mL/min) = { (140 – age (years)) x weight (kg) x constant*} /
        serum creatinine (μmol/L)

        *constant = 1.23 for males and 1.05 for females
        """  # noqa: RUF002
        if self.gender and self.age_in_years and self.weight and self.creatinine_value:
            gender_factor = 1.05 if self.gender == self.female else 1.23
            adjusted_age = 140.00 - self.age_in_years
            return (adjusted_age * self.weight * gender_factor) / float(self.creatinine_value)
        opts = dict(
            gender=self.gender,
            age_in_years=self.age_in_years,
            weight=self.weight,
            creatinine_value=self.creatinine_value,
        )
        raise EgfrCalculatorError(
            f"Unable to calculate egfr_value. Insufficient information. Got {opts}."
        )
