from __future__ import annotations

import pandas as pd

from ..dataframe import (
    coerce_date_columns,
    convert_and_clean_string_columns,
    convert_numeric_columns,
    convert_visit_code_to_float,
)


def get_df_subject_visit(table_name: str, db_name: str, db_conn) -> pd.DataFrame:
    df = pd.read_sql(f"select * from {table_name}", db_conn)  # noqa: S608
    df = df.rename(
        columns={
            "id": "subject_visit_id",
            "report_datetime": "visit_datetime",
            "reason": "visit_reason",
        }
    )
    df = coerce_date_columns(df, table_name, db_name, db_conn)
    df = convert_numeric_columns(df, table_name, db_name, db_conn)
    df = convert_and_clean_string_columns(df, table_name, db_name, db_conn)
    return convert_visit_code_to_float(df)
