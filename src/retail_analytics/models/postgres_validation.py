from dataclasses import dataclass


@dataclass(frozen=True)
class PostgresLoadValidationResult:
    source_name: str
    source_run_date: str
    source_file: str
    cleaned_file_path: str
    target_schema: str
    target_table: str
    table_exists: bool
    source_row_count: int | None
    table_row_count: int | None
    latest_audit_status: str | None
    latest_audit_loaded_row_count: int | None
    status: str
    message: str
    validated_at: str