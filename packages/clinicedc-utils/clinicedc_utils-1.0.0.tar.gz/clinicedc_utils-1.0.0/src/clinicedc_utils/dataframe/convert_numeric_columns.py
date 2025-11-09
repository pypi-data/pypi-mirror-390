from __future__ import annotations

import pandas as pd


def convert_numeric_columns(df, table_name=None, db_name=None, db_conn=None) -> pd.DataFrame:
    data_types = ("int", "decimal")
    data_types_str = "','".join(data_types)
    cols_sql = (
        "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "  # noqa: S608
        f"WHERE TABLE_SCHEMA = '{db_name}' AND TABLE_NAME = '{table_name}' AND "
        f"DATA_TYPE IN ('{data_types_str}');"
    )
    df_cols = pd.read_sql(cols_sql, db_conn)
    cols = df_cols["COLUMN_NAME"].tolist()
    for col in cols:
        if col in df.columns and df[col].dtype == "object":
            df[col] = pd.to_numeric(df[col])
    return df
