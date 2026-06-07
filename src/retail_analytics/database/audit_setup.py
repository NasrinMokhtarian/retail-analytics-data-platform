import logging
from retail_analytics.database.connection import get_postgres_connection

logger = logging.getLogger(__name__)

CREATE_LOAD_AUDIT_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS audit.load_audit (
        load_id BIGSERIAL PRIMARY KEY,
        run_date DATE NOT NULL,
        source_name TEXT NOT NULL,
        source_file TEXT NOT NULL,
        target_schema TEXT NOT NULL,
        target_table TEXT NOT NULL,
        source_row_count INTEGER,
        loaded_row_count INTEGER,
        load_started_at TIMESTAMPTZ NOT NULL,
        load_finished_at TIMESTAMPTZ,
        status TEXT NOT NULL,
        error_message TEXT,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
"""

def create_load_audit_table() -> None:
    """
    Create the audit.load_audit table.

    This table tracks file-to-PostgreSQL load attempts.
    """

    logger.info("Creating audit.load_audit table if it does not exist")
    with get_postgres_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(CREATE_LOAD_AUDIT_TABLE_SQL)

        conn.commit()
    logger.info("audit.load_audit table created or already exists")

def verify_load_audit_table() -> None:
    """
    Verify that audit.load_audit exists.
    """

    verify_sql = """
    SELECT EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'audit'
          AND table_name = 'load_audit'
    );
    """
    with get_postgres_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(verify_sql)
            exists = cursor.fetchone()[0]
    if not exists:
        raise RuntimeError("audit.load_audit table was not created successfully")

    logger.info("audit.load_audit table verified successfully")