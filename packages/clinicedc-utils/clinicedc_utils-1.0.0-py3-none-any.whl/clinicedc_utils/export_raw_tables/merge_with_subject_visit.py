from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def merge_with_subject_visit(df, df_visit) -> pd.DataFrame:
    return df.merge(
        df_visit[
            [
                "subject_identifier",
                "subject_visit_id",
                "visit_datetime",
                "visit_code",
                "visit_reason",
            ]
        ],
        on="subject_visit_id",
        how="left",
    )
