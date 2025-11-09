from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def convert_visit_code_to_float(df: pd.Dataframe) -> pd.Dataframe:
    """Convert visit_code to float using visit_code_sequence"""
    if df["visit_code"].dtype == "object":
        df["visit_code_str"] = df["visit_code"]
        df["visit_code_sequence_new"] = df["visit_code_sequence"]
        df["visit_code_sequence_new"] = (
            df["visit_code_sequence_new"]
            .astype(float)
            .apply(lambda x: x / 10.0 if x > 0.0 else 0.0)
        )
        df["visit_code"] = df["visit_code"].astype(float)
        df["visit_code"] = df["visit_code"] + df["visit_code_sequence_new"]
        df["visit_code"] = df["visit_code"].astype(float)
        return df.drop(columns=["visit_code_sequence_new"])
    return df
