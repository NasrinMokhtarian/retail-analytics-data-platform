from __future__ import annotations
import logging
from dataclasses import dataclass
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class ReportGateResult:
    report_path: Path
    total_checks: int
    passed_checks: int
    failed_checks: int
    error_failures: int
    warning_failures: int

def normalize_text_value(value:object) -> str:
    if pd.isna(value):
        return""
    return str(value).strip().lower()

def chack_report_gate(report_path:Path) -> ReportGateResult:
    if not report_path.exists():
        raise FileNotFoundError(f"Report file does not exist: {report_path}")
    report_df = pd.read_csv(report_path)
    required_columns = {"status","severity"}
    missing_columns = required_columns - set(report_df.columns)

    if missing_columns:
        raise ValueError(f"Report {report_path} is missing required columns:",
                         f"{sorted(missing_columns)}")
    normalized_status = report_df['status'].map(normalize_text_value)
    normalized_severity = report_df["severity"].map(normalize_text_value)
    failed_mask = normalized_status == "fail"
    error_failure_mask = failed_mask & (normalized_severity == "error")
    warning_failure_mask = failed_mask & (normalized_severity == "warning")

    result = ReportGateResult(
        report_path=report_path,
        total_checks=len(report_df),
        passed_checks=int((normalized_status == "pass").sum()),
        failed_checks=int(failed_mask.sum()),
        error_failures=int(error_failure_mask.sum()),
        warning_failures=int(warning_failure_mask.sum()),
    )

    logger.info(
        "Report gate evaluated",
        extra={
            "report_path": str(report_path),
            "total_checks": result.total_checks,
            "passed_checks": result.passed_checks,
            "failed_checks": result.failed_checks,
            "error_failures": result.error_failures,
            "warning_failures": result.warning_failures,
        },
    )

    if result.error_failures > 0:
        failed_rows = report_df.loc[error_failure_mask].copy()

        preview_columns = [
            column
            for column in [
                "rule_id",
                "check_id",
                "status",
                "severity",
                "failed_count",
                "total_count",
                "message",
            ]
            if column in failed_rows.columns
        ]

        failure_preview = failed_rows[preview_columns].to_string(index=False)

        raise RuntimeError(
            "Report gate failed because error-level failures were found in "
            f"{report_path}.\n\n{failure_preview}"
        )

    return result
