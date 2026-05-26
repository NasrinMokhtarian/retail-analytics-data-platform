from dataclasses import dataclass

@dataclass(frozen=True)

class RawQualityCheckResult:
    rule_id: str
    source_file: str
    column_name: str |None
    rule_type: str
    severity: str
    status: str
    failed_count: int
    total_count: int
    failure_percentage: float
    message: str
    checked_at: str
    