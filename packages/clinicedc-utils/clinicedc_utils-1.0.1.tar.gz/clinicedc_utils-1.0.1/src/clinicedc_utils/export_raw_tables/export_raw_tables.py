from __future__ import annotations

from pathlib import Path

import pandas as pd
from remote_read_sql import get_db_connection, remote_connect
from sqlalchemy.exc import OperationalError
from tqdm import tqdm

from ..dataframe import (
    coerce_date_columns,
    convert_and_clean_string_columns,
    convert_numeric_columns,
    convert_visit_code_to_float,
)
from .get_df_subject_consent import get_df_subject_consent
from .get_df_subject_visit import get_df_subject_visit
from .merge_with_subject_consent import merge_with_subject_consent
from .merge_with_subject_visit import merge_with_subject_visit


def export_raw_tables(
    subject_visit_table: str | None = None,
    subject_consent_table: str | None = None,
    data_folder: Path | None = None,
    ssh_config_path: Path | None = None,
    my_cnf_path: Path | None = None,
    my_cnf_connection_name: str | None = None,
    db_name: str | None = None,
    include_tables: list[str] | None = None,
    exclude_tables: list[str] | None = None,
) -> dict:
    """Export raw tables to CSV and DTA to the given data folder.

    db_conn options might look like this:
      ssh_config_path = Path("~/.remote_read_sql")
      my_cnf_path = Path("~/.my.cnf")
      my_cnf_connection_name = "remote"
      data_folder = Path("~/data/raw_tables").expanduser()
      db_name = "meta3_production"

    See remote_read_sql for required attributes for tunnel connection.
    https://github.com/erikvw/remote-read-sql

    Add your conn options to a dict:

    db_conn_opts = dict(
        ssh_config_path=ssh_config_path,
        my_cnf_path=my_cnf_path,
        my_cnf_connection_name=my_cnf_connection_name,
        db_name=db_name
    )

    and call like this:

    problems = export_raw_tables(
        data_folder=data_folder,
        subject_visit_table="meta_subject_subjectvisit",
        subject_consent_table="meta_consent_subjectconsent",
        **db_conn_opts
    )

    Note: this func does not follow relations for FK and M2M fields.

    """
    problems = []
    if ssh_config_path:
        conn_opts = dict(
            ssh_config_path=ssh_config_path,
            my_cnf_path=my_cnf_path,
            my_cnf_connection_name=my_cnf_connection_name,
            db_name=db_name,
        )
        with remote_connect(**conn_opts) as db_conn:
            problems = _export_raw_tables(
                db_conn,
                subject_visit_table,
                subject_consent_table,
                data_folder,
                db_name,
                include_tables,
                exclude_tables,
            )
    else:
        conn_opts = dict(
            my_cnf_path=my_cnf_path,
            local_bind_port=3306,
            my_cnf_connection_name=my_cnf_connection_name,
            db_name=db_name,
        )
        with get_db_connection(**conn_opts) as db_conn:
            problems = _export_raw_tables(
                db_conn,
                subject_visit_table,
                subject_consent_table,
                data_folder,
                db_name,
                include_tables,
                exclude_tables,
            )
    return problems


def _export_raw_tables(
    db_conn,
    subject_visit_table: str,
    subject_consent_table: str,
    data_folder: Path,
    db_name: str,
    include_tables: list[str] | None = None,
    exclude_tables: list[str] | None = None,
):
    df_subject_visit = get_df_subject_visit(subject_visit_table, db_name, db_conn)
    df_subject_consent = get_df_subject_consent(subject_consent_table, db_name, db_conn)
    df_tables = pd.read_sql("show tables;", db_conn)
    df_tables = df_tables.rename(columns={f"Tables_in_{db_name}": "tables"})
    df_tables = df_tables[
        ~(df_tables["tables"].str.startswith("auth"))
        & ~(df_tables["tables"].str.startswith("django"))
        & ~(df_tables["tables"].str.contains("rando"))
        & ~(df_tables["tables"].str.contains("canned"))
        & ~(df_tables["tables"].str.contains("edcpermissions"))
        & ~(df_tables["tables"].str.startswith("edc_auth"))
        & ~(df_tables["tables"].str.contains("historical"))
        & ~(df_tables["tables"].str.startswith("edc_lab"))
        & ~(df_tables["tables"].str.startswith("edc_pharmacy"))
        & ~(df_tables["tables"].str.startswith("edc_export"))
    ]
    total = len(df_tables)
    problems = {}
    for table_name in tqdm(df_tables["tables"], total=total):
        if include_tables and table_name not in include_tables:
            continue
        if exclude_tables and table_name in exclude_tables:
            continue
        csv_path = data_folder / f"{table_name}.csv"
        dta_path = data_folder / f"{table_name}.dta"
        sql_query = f"select * from {table_name} order by created;"  # noqa: S608
        try:
            df = pd.read_sql(sql_query, db_conn)
        except OperationalError:
            sql_query = f"select * from {table_name};"  # noqa: S608
            df = pd.read_sql(sql_query, db_conn)
            csv_path = data_folder / "other" / f"{table_name}.csv"
            dta_path = data_folder / "other" / f"{table_name}.dta"
        finally:
            df = coerce_date_columns(df, table_name, db_name, db_conn)
            df = convert_numeric_columns(df, table_name, db_name, db_conn)
            df = convert_and_clean_string_columns(df, table_name, db_name, db_conn)
            if "visit_code" in df.columns:
                df = convert_visit_code_to_float(df_subject_visit)
            if "subject_visit_id" in df.columns and table_name not in [
                "edc_appointment_appointment",
                subject_visit_table,
            ]:
                df = merge_with_subject_visit(df, df_subject_visit)

            if "subject_identifier" in df.columns and table_name != subject_consent_table:
                df = merge_with_subject_consent(df, df_subject_consent)

            df.to_csv(csv_path, sep="|", encoding="utf-8", index=False)
            try:
                df.to_stata(path=dta_path, version=118, write_index=False)
            except ValueError as e:
                problems.update({table_name: str(e)})
    return problems
