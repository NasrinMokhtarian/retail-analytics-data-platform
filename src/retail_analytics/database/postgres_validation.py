import logging
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from psycopg2 import sql

from retail_analytics.database.connection import get_postgres_connection
from retail_analytics.database.load_config import (
    PostgresLoadTarget,
    build_selected_load_targets,
)
from retail_analytics.models.postgres_validation import PostgresLoadValidationResult

logger = logging.getLogger(__name__)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def table_exists(target_schema: str, target_table: str) -> bool:
    query = """
    SELECT EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = %s
          AND table_name = %s
    );
    """

    with get_postgres_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (target_schema, target_table))
            exists = cursor.fetchone()[0]

    return bool(exists)


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


def get_latest_audit_record(
    run_date: str,
    source_name: str,
    source_file: str,
    target_schema: str,
    target_table: str,
) -> dict | None:
    query = """
        SELECT
            status,
            loaded_row_count
        FROM audit.load_audit
        WHERE run_date = %s
        AND source_name = %s
        AND source_file = %s
        AND target_schema = %s
        AND target_table = %s
        ORDER BY
            load_finished_at DESC NULLS LAST,
            load_started_at DESC NULLS LAST
        LIMIT 1;
    """

    with get_postgres_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                query,
                (
                    run_date,
                    source_name,
                    source_file,
                    target_schema,
                    target_table,
                ),
            )

            row = cursor.fetchone()

    if row is None:
        return None

    return {
        "status": row[0],
        "loaded_row_count": row[1],
    }


def count_csv_rows(csv_path: Path) -> int:
    df = pd.read_csv(csv_path)
    return len(df)


def validate_single_load_target(
    load_target: PostgresLoadTarget,
) -> PostgresLoadValidationResult:
    logger.info(
        "Validating PostgreSQL load target",
        extra=asdict(load_target),
    )

    cleaned_file_exists = load_target.cleaned_file_path.exists()

    if not cleaned_file_exists:
        return PostgresLoadValidationResult(
            source_name=load_target.source_name,
            source_run_date=load_target.source_run_date,
            source_file=load_target.source_file,
            cleaned_file_path=str(load_target.cleaned_file_path),
            target_schema=load_target.target_schema,
            target_table=load_target.target_table,
            table_exists=False,
            source_row_count=None,
            table_row_count=None,
            latest_audit_status=None,
            latest_audit_loaded_row_count=None,
            status="FAIL",
            message=f"Cleaned file is missing: {load_target.cleaned_file_path}",
            validated_at=utc_now(),
        )

    source_row_count = count_csv_rows(load_target.cleaned_file_path)

    db_table_exists = table_exists(
        target_schema=load_target.target_schema,
        target_table=load_target.target_table,
    )

    if not db_table_exists:
        return PostgresLoadValidationResult(
            source_name=load_target.source_name,
            source_run_date=load_target.source_run_date,
            source_file=load_target.source_file,
            cleaned_file_path=str(load_target.cleaned_file_path),
            target_schema=load_target.target_schema,
            target_table=load_target.target_table,
            table_exists=False,
            source_row_count=source_row_count,
            table_row_count=None,
            latest_audit_status=None,
            latest_audit_loaded_row_count=None,
            status="FAIL",
            message=(
                f"Target table is missing: "
                f"{load_target.target_schema}.{load_target.target_table}"
            ),
            validated_at=utc_now(),
        )

    table_row_count = count_table_rows(
        target_schema=load_target.target_schema,
        target_table=load_target.target_table,
    )

    latest_audit_record = get_latest_audit_record(
        run_date=load_target.source_run_date,
        source_name=load_target.source_name,
        source_file=load_target.source_file,
        target_schema=load_target.target_schema,
        target_table=load_target.target_table,
    )

    if latest_audit_record is None:
        return PostgresLoadValidationResult(
            source_name=load_target.source_name,
            source_run_date=load_target.source_run_date,
            source_file=load_target.source_file,
            cleaned_file_path=str(load_target.cleaned_file_path),
            target_schema=load_target.target_schema,
            target_table=load_target.target_table,
            table_exists=True,
            source_row_count=source_row_count,
            table_row_count=table_row_count,
            latest_audit_status=None,
            latest_audit_loaded_row_count=None,
            status="FAIL",
            message="No audit record found for this load target",
            validated_at=utc_now(),
        )

    latest_audit_status = latest_audit_record["status"]
    latest_audit_loaded_row_count = latest_audit_record["loaded_row_count"]

    checks_passed = (
        source_row_count == table_row_count
        and latest_audit_status == "SUCCESS"
        and latest_audit_loaded_row_count == table_row_count
    )

    if checks_passed:
        status = "PASS"
        message = "Source file, PostgreSQL table, and audit row counts match"
    else:
        status = "FAIL"
        message = (
            "Validation failed: "
            f"source_row_count={source_row_count}, "
            f"table_row_count={table_row_count}, "
            f"latest_audit_status={latest_audit_status}, "
            f"latest_audit_loaded_row_count={latest_audit_loaded_row_count}"
        )

    return PostgresLoadValidationResult(
        source_name=load_target.source_name,
        source_run_date=load_target.source_run_date,
        source_file=load_target.source_file,
        cleaned_file_path=str(load_target.cleaned_file_path),
        target_schema=load_target.target_schema,
        target_table=load_target.target_table,
        table_exists=True,
        source_row_count=source_row_count,
        table_row_count=table_row_count,
        latest_audit_status=latest_audit_status,
        latest_audit_loaded_row_count=latest_audit_loaded_row_count,
        status=status,
        message=message,
        validated_at=utc_now(),
    )


def validate_postgres_loads(
    output_dir: Path,
    validation_run_date: str,
    selected_sources: list[str],
    olist_run_date: str | None = None,
    supplier_run_date: str | None = None,
    br_holidays_run_date: str | None = None,
) -> Path:
    load_targets = build_selected_load_targets(
        selected_sources=selected_sources,
        olist_run_date=olist_run_date,
        supplier_run_date=supplier_run_date,
        br_holidays_run_date=br_holidays_run_date,
    )

    logger.info(
        "PostgreSQL load validation started",
        extra={
            "selected_sources": selected_sources,
            "olist_run_date": olist_run_date,
            "supplier_run_date": supplier_run_date,
            "br_holidays_run_date": br_holidays_run_date,
            "validation_run_date": validation_run_date,
            "load_target_count": len(load_targets),
        },
    )

    validation_results = [
        validate_single_load_target(load_target)
        for load_target in load_targets
    ]

    run_output_dir = output_dir / f"run_date={validation_run_date}"
    run_output_dir.mkdir(parents=True, exist_ok=True)

    output_file = run_output_dir / "postgres_load_validation_report.csv"

    output_columns = [
        "source_name",
        "source_run_date",
        "source_file",
        "cleaned_file_path",
        "target_schema",
        "target_table",
        "table_exists",
        "source_row_count",
        "table_row_count",
        "latest_audit_status",
        "latest_audit_loaded_row_count",
        "status",
        "severity",
        "message",
        "validated_at",
    ]

    validation_df = pd.DataFrame(
        asdict(result) for result in validation_results
    )

    # Make this report compatible with check_report_gates.py.
    # Any PostgreSQL load validation failure should stop the pipeline.
    validation_df["severity"] = "error"

    validation_df = validation_df[output_columns]
    validation_df.to_csv(output_file, index=False)

    failed_count = int((validation_df["status"] == "FAIL").sum())

    logger.info(
        "PostgreSQL load validation completed",
        extra={
            "output_file": str(output_file),
            "validated_target_count": len(validation_df),
            "failed_count": failed_count,
        },
    )

    return output_file