from __future__ import annotations

import pandas as pd


def coerce_date_columns(df, table_name=None, db_name=None, db_conn=None) -> pd.DataFrame:
    data_types = ("date", "datetime", "timestamp", "year")
    data_types_str = "','".join(data_types)
    date_cols_sql = (
        "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "  # noqa: S608
        f"WHERE TABLE_SCHEMA = '{db_name}' AND TABLE_NAME = '{table_name}' AND "
        f"DATA_TYPE IN ('{data_types_str}');"
    )
    df_date_cols = pd.read_sql(date_cols_sql, db_conn)
    date_cols = df_date_cols["COLUMN_NAME"].tolist()
    for col in date_cols:
        if col in df.columns and df[col].dtype == "object":
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df
