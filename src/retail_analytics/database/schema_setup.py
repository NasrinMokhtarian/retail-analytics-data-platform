import logging
from retail_analytics.database.connection import get_postgres_connection

logger = logging.getLogger(__name__)
SCHEMAS = ['raw', 'staging', 'mart', 'audit']


def create_database_schemas() -> None:
    """
    Create required PostgreSQL schemas for the project.

    Schemas:
    - raw: source-like loaded tables
    - staging: cleaned SQL transformation layer
    - mart: business-ready analytical tables
    - audit: pipeline/load tracking
    """

    logger.info(
        "PostgreSQL schema creation started",
        extra={"schemas": SCHEMAS},
    )

    with get_postgres_connection() as conn:
        with conn.cursor() as cursor:
            for schema_name in SCHEMAS:
                cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name};")

        conn.commit()

    logger.info(
        "PostgreSQL schema creation completed",
        extra={"schemas": SCHEMAS},
    )

def get_existing_project_schemas() -> list[str]:
    with get_postgres_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT schema_name
                FROM information_schema.schemata
                WHERE schema_name IN ('raw', 'staging', 'mart', 'audit')
                ORDER BY schema_name;
                """
            )

            rows = cursor.fetchall()

    return [row[0] for row in rows]

def verify_database_schemas() -> None:
    existing_schemas = get_existing_project_schemas()
    missing_schemas = sorted(set(SCHEMAS) - set(existing_schemas))

    if missing_schemas:
        raise RuntimeError(f"Missing expected schemas: {missing_schemas}")

    logger.info(
        "PostgreSQL schemas verified successfully",
        extra={"existing_schemas": existing_schemas},
    )
     