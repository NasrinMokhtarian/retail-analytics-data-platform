from dataclasses import dataclass


@dataclass(frozen=True)
class CleaningValidationResult:
    check_id: str
    source_file: str
    cleaned_file: str
    check_type: str
    severity: str
    status: str
    raw_row_count: int | None
    cleaned_row_count: int | None
    failed_count: int
    total_count: int
    message: str
    validated_at: str