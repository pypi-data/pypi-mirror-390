"""

https://www.kidney.org/ckd-epi-creatinine-equation-2021
"""

from __future__ import annotations

from clinicedc_constants import BLACK

from clinicedc_utils import convert_units

from .base_egfr import BaseEgfr, EgfrCalculatorError

# TODO: https://www.rcpa.edu.au/Manuals/RCPA-Manual/
#  Pathology-Tests/C/Creatinine-clearance-Cockcroft-and-Gault

__all__ = ["EgfrCkdEpi2021"]


class EgfrCkdEpi2021(BaseEgfr):
    """
    CKD-EPI Creatinine equation (2021)

    eGFR = 142 *
           min(standardized Scr/K, 1)α *
           max(standardized Scr/K, 1)-1.200 *
           0.9938Age * 1.012 [if female]

    eGFR (estimated glomerular filtration rate) = mL/min/ 1.73 m2
    Scr (serum creatinine) = mg/dL
    K = 0.7 (females) or 0.9 (males)
    α = -0.241 (females) or -0.302 (males)
    min = indicates the minimum of Scr/K or 1
    max = indicates the maximum of Scr/K or 1

    https://www.kidney.org/ckd-epi-creatinine-equation-2021
    """  # noqa: RUF002

    black = BLACK

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.creatinine_units == self.micromoles_per_liter:
            self.creatinine_value = convert_units(
                label="creatinine",
                value=float(self.creatinine_value),
                units_from=self.creatinine_units,
                units_to=self.milligrams_per_deciliter,
                mw=self.mw_creatinine,
            )

    @property
    def value(self) -> float | None:
        if self.gender and self.age_in_years and self.creatinine_value:
            return float(
                142.000
                * (min(self.creatinine_value / self.kappa, 1.000) ** self.alpha)
                * (max(self.creatinine_value / self.kappa, 1.000) ** -1.200)
                * self.age_factor
                * self.gender_factor
            )
        opts = dict(
            gender=self.gender,
            age_in_years=self.age_in_years,
            creatinine_value=self.creatinine_value,
        )
        raise EgfrCalculatorError(f"Unable to calculate. Insufficient information. Got {opts}")

    @property
    def alpha(self) -> float:
        """-0.241 (females) or -0.302 (males)"""
        return float(-0.241 if self.gender == self.female else -0.302)

    @property
    def kappa(self) -> float:
        """0.7 (females) or 0.9 (males)"""
        return float(0.7 if self.gender == self.female else 0.9)

    @property
    def gender_factor(self) -> float:
        """* 1.012 [if female]"""
        return float(1.012 if self.gender == self.female else 1.000)

    @property
    def age_factor(self) -> float:
        """0.9938Age"""
        return float(0.993**self.age_in_years)
