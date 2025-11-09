from __future__ import annotations

from clinicedc_constants import BLACK

from clinicedc_utils import convert_units

from .base_egfr import BaseEgfr, EgfrCalculatorError

# TODO: https://www.rcpa.edu.au/Manuals/RCPA-Manual/
#  Pathology-Tests/C/Creatinine-clearance-Cockcroft-and-Gault

__all__ = ["EgfrCkdEpi2009"]


class EgfrCkdEpi2009(BaseEgfr):
    """Reference https://nephron.com/epi_equation

    CKD-EPI Creatinine equation (2009)

    Levey AS, Stevens LA, et al. A New Equation to Estimate Glomerular
    Filtration Rate. Ann Intern Med. 2009; 150:604-612.
    """

    black = BLACK

    def __init__(self, *, ethnicity: str, **kwargs):
        super().__init__(**kwargs)
        self.ethnicity = ethnicity
        if self.creatinine_units == self.micromoles_per_liter:
            self.creatinine_value = convert_units(
                label="creatinine",
                value=float(self.creatinine_value),
                units_from=self.creatinine_units,
                units_to=self.milligrams_per_deciliter,
                mw=self.mw_creatinine,
            )
        else:
            self.creatinine_value = float(self.creatinine_value)

    @property
    def value(self) -> float | None:
        if self.gender and self.age_in_years and self.ethnicity and self.creatinine_value:
            return float(
                141.000
                * (min(self.creatinine_value / self.kappa, 1.000) ** self.alpha)
                * (max(self.creatinine_value / self.kappa, 1.000) ** -1.209)
                * self.age_factor
                * self.gender_factor
                * self.ethnicity_factor
            )
        opts = dict(
            gender=self.gender,
            age_in_years=self.age_in_years,
            ethnicity=self.ethnicity,
            creatinine_value=self.creatinine_value,
        )
        raise EgfrCalculatorError(f"Unable to calculate. Insufficient information. Got {opts}")

    @property
    def alpha(self) -> float:
        return float(-0.329 if self.gender == self.female else -0.411)

    @property
    def kappa(self) -> float:
        return float(0.7 if self.gender == self.female else 0.9)

    @property
    def ethnicity_factor(self) -> float:
        return float(1.159 if self.ethnicity == self.black else 1.000)

    @property
    def gender_factor(self) -> float:
        return float(1.018 if self.gender == self.female else 1.000)

    @property
    def age_factor(self) -> float:
        return float(0.993**self.age_in_years)
