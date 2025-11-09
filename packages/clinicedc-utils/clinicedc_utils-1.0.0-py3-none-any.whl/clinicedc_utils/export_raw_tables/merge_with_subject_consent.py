from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def merge_with_subject_consent(df, df_consent) -> pd.DataFrame:
    return df.merge(
        df_consent[["subject_identifier", "gender", "dob", "screening_identifier"]],
        on="subject_identifier",
        how="left",
    )
