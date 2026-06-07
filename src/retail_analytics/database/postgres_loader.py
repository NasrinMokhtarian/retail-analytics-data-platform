import logging
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
from psycopg2 import sql
from retail_analytics.database.connection import  get_postgres_connection,get_sqlalchemy_engine

from retail_analytics.database.load_config import PostgresLoadTarget,build_all_load_targets,validate_load_target_files_exist

logger = logging.getLogger(__name__)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
def count_table_rows(target_schema: str, target_table: str) -> int:
    with get_postgres_connection() as conn:
        with conn.cursor() as cursor:
            query = sql.SQL("SELECT COUNT(*) FROM {}.{}").format(
                sql.Identifier(target_schema),
                sql.Identifier(target_table),
            )
            cursor.execute(query)
            row_count = cursor.fetchone()[0]

    return int(row_count)

def insert_load_audit_record(
    run_date: str,
    source_name: str,
    source_file: str,
    target_schema: str,
    target_table: str,
    source_row_count: int | None,
    loaded_row_count: int | None,
    load_started_at: datetime,
    load_finished_at: datetime,
    status: str,
    error_message: str | None,
) -> None:
    insert_sql = """
    INSERT INTO audit.load_audit (
        run_date,
        source_name,
        source_file,
        target_schema,
        target_table,
        source_row_count,
        loaded_row_count,
        load_started_at,
        load_finished_at,
        status,
        error_message
    )
    VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    );
    """

    with get_postgres_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                insert_sql,
                (
                    run_date,
                    source_name,
                    source_file,
                    target_schema,
                    target_table,
                    source_row_count,
                    loaded_row_count,
                    load_started_at,
                    load_finished_at,
                    status,
                    error_message,
                ),
            )

        conn.commit()
    
def load_single_target(load_target: PostgresLoadTarget) -> None:
    load_started_at = utc_now()
    source_row_count: int | None = None
    loaded_row_count: int | None = None

    logger.info(
        "PostgreSQL table load started",
        extra=asdict(load_target),
    )

    try:
        df = pd.read_csv(load_target.cleaned_file_path)
        source_row_count = len(df)

        engine = get_sqlalchemy_engine()

        df.to_sql(
            name=load_target.target_table,
            con=engine,
            schema=load_target.target_schema,
            if_exists="replace",
            index=False,
            method="multi",
            chunksize=10_000,
        )

        loaded_row_count = count_table_rows(
            target_schema=load_target.target_schema,
            target_table=load_target.target_table,
        )

        if source_row_count != loaded_row_count:
            raise RuntimeError(
                "Row count mismatch after PostgreSQL load: "
                f"source_row_count={source_row_count}, "
                f"loaded_row_count={loaded_row_count}, "
                f"target={load_target.target_schema}.{load_target.target_table}"
            )

        load_finished_at = utc_now()

        insert_load_audit_record(
            run_date=load_target.source_run_date,
            source_name=load_target.source_name,
            source_file=load_target.source_file,
            target_schema=load_target.target_schema,
            target_table=load_target.target_table,
            source_row_count=source_row_count,
            loaded_row_count=loaded_row_count,
            load_started_at=load_started_at,
            load_finished_at=load_finished_at,
            status="SUCCESS",
            error_message=None,
        )

        logger.info(
            "PostgreSQL table load completed successfully",
            extra={
                **asdict(load_target),
                "source_row_count": source_row_count,
                "loaded_row_count": loaded_row_count,
            },
        )

    except Exception as exc:
        load_finished_at = utc_now()

        try:
            insert_load_audit_record(
                run_date=load_target.source_run_date,
                source_name=load_target.source_name,
                source_file=load_target.source_file,
                target_schema=load_target.target_schema,
                target_table=load_target.target_table,
                source_row_count=source_row_count,
                loaded_row_count=loaded_row_count,
                load_started_at=load_started_at,
                load_finished_at=load_finished_at,
                status="FAILED",
                error_message=str(exc),
            )
        except Exception:
            logger.exception(
                "Failed to write load failure to audit table",
                extra=asdict(load_target),
            )

        logger.exception(
            "PostgreSQL table load failed",
            extra={
                **asdict(load_target),
                "source_row_count": source_row_count,
                "loaded_row_count": loaded_row_count,
                "error_message": str(exc),
            },
        )

        raise


def load_cleaned_files_to_postgres(olist_run_date: str,supplier_run_date: str) -> None:
    load_targets = build_all_load_targets(
        olist_run_date=olist_run_date,
        supplier_run_date=supplier_run_date,
    )

    validate_load_target_files_exist(load_targets)

    logger.info(
        "PostgreSQL cleaned file load started",
        extra={
            "olist_run_date": olist_run_date,
            "supplier_run_date": supplier_run_date,
            "load_target_count": len(load_targets),
        },
    )

    for load_target in load_targets:
        load_single_target(load_target)

    logger.info(
        "PostgreSQL cleaned file load completed successfully",
        extra={"load_target_count": len(load_targets)},
    )