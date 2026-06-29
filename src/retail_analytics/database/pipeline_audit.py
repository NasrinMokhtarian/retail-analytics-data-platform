from __future__ import annotations

from datetime import datetime, timezone

from retail_analytics.database.connection import get_postgres_connection


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def ensure_pipeline_runs_table_exists() -> None:
    create_sql = """
    CREATE SCHEMA IF NOT EXISTS audit;

    CREATE TABLE IF NOT EXISTS audit.pipeline_runs (
        pipeline_run_id BIGSERIAL PRIMARY KEY,
        pipeline_name TEXT NOT NULL,
        run_date DATE NOT NULL,
        selected_sources TEXT,
        started_at TIMESTAMPTZ NOT NULL,
        finished_at TIMESTAMPTZ,
        status TEXT NOT NULL,
        error_message TEXT
    );
    """

    with get_postgres_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(create_sql)

        conn.commit()


def start_pipeline_run(
    pipeline_name: str,
    run_date: str,
    selected_sources: list[str] | None = None,
) -> int:
    ensure_pipeline_runs_table_exists()

    selected_sources_value = None
    if selected_sources:
        selected_sources_value = ",".join(selected_sources)

    insert_sql = """
    INSERT INTO audit.pipeline_runs (
        pipeline_name,
        run_date,
        selected_sources,
        started_at,
        status
    )
    VALUES (%s, %s, %s, %s, %s)
    RETURNING pipeline_run_id;
    """

    with get_postgres_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                insert_sql,
                (
                    pipeline_name,
                    run_date,
                    selected_sources_value,
                    utc_now(),
                    "STARTED",
                ),
            )

            pipeline_run_id = cursor.fetchone()[0]

        conn.commit()

    return int(pipeline_run_id)


def finish_pipeline_run(
    pipeline_run_id: int,
    status: str,
    error_message: str | None = None,
) -> None:
    allowed_statuses = {"SUCCESS", "FAILED"}

    if status not in allowed_statuses:
        raise ValueError(
            f"Invalid pipeline status: {status}. "
            f"Expected one of: {sorted(allowed_statuses)}"
        )

    ensure_pipeline_runs_table_exists()

    update_sql = """
    UPDATE audit.pipeline_runs
    SET
        finished_at = %s,
        status = %s,
        error_message = %s
    WHERE pipeline_run_id = %s;
    """

    with get_postgres_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                update_sql,
                (
                    utc_now(),
                    status,
                    error_message,
                    pipeline_run_id,
                ),
            )

            if cursor.rowcount != 1:
                raise RuntimeError(
                    f"No pipeline run found for pipeline_run_id={pipeline_run_id}"
                )

        conn.commit()