from __future__ import annotations
import logging
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd # type: ignore[import]
from retail_analytics.models.raw_quality import RawQualityCheckResult
from retail_analytics.config import DEFAULT_BR_HOLIDAYS_CLEAN_FILE,EXPECTED_HOLIDAY_YEARS,EXPECTED_COUNTRY_CODE

logger = logging.getLogger(__name__)

EXPECTED_COLUMNS = [
    "holiday_date",
    "holiday_name",
    "holiday_local_name",
    "country_code",
    "is_fixed",
    "is_global",
    "counties",
    "launch_year",
    "holiday_types",
    "source_system",
    "source_file_name",
    "extracted_at",
    "run_date",
]
def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def calculate_failure_percentage(failed_count: int, total_count: int) -> float:
    if total_count== 0:
        return 0.0
    return round((failed_count/total_count)*100,2)

def build_result(
    rule_id: str,
    source_file: str,
    column_name: str | None,
    rule_type: str,
    severity: str,
    failed_count: int,
    total_count: int,
    message: str,
) -> RawQualityCheckResult:
    status = "PASS" if failed_count==0 else "FAIL"
    return RawQualityCheckResult(
        rule_id=rule_id,
        source_file=source_file,
        column_name=column_name,
        rule_type=rule_type,
        severity=severity,
        status=status,
        failed_count=failed_count,
        total_count=total_count,
        failure_percentage=calculate_failure_percentage(
            failed_count=failed_count,
            total_count=total_count,
        ),
        message=message,
        checked_at=utc_now(),
    )
def normalize_text_series(series: pd.Series) -> pd.Series:
    return series.astype("string").str.strip().replace("", pd.NA)

def check_clean_file_exists(
    clean_data_dir: Path,
    run_date: str,
    source_file: str,
) -> RawQualityCheckResult:
    file_path = clean_data_dir / f"run_date={run_date}" / source_file
    file_exists = file_path.exists()

    return build_result(
        rule_id="BR_HOL_DQ_FILE_EXISTS_001",
        source_file=source_file,
        column_name=None,
        rule_type="file_exists",
        severity="error",
        failed_count=0 if file_exists else 1,
        total_count=1,
        message=(
            "Br holidays cleaned file exists."
            if file_exists
            else f"Br holidays cleaned file is missing: {file_path}"
        ),
    )
def check_file_not_empty(df:pd.DataFrame,source_file: str) -> RawQualityCheckResult:
    row_count = len(df)
    failed_count = 1 if row_count == 0 else 0

    return build_result(
        rule_id = "BR_HOL_DQ_NOT_EMPTY_001",
        source_file=source_file,
        column_name=None,
        rule_type="not_empty",
        severity="error",
        failed_count=failed_count,
        total_count=1,
        message=(
            f"Brholidays cleaned file is not empty. rows={row_count}"
            if failed_count == 0
            else "Br holidays cleaned file is empty."
        ),
    )
def check_required_columns( df: pd.DataFrame, source_file: str) -> list[RawQualityCheckResult]:
    results: list[RawQualityCheckResult]=[]
    actual_columns = set(df.columns)

    for column_name in EXPECTED_COLUMNS:
        column_exists = column_name in actual_columns
        results.append(
            build_result(
                rule_id=f"BR_HOL_DQ_REQUIRED_COLUMN_{column_name.upper()}",
                source_file=source_file,
                column_name=column_name,
                rule_type="required_column_exists",
                severity="error",
                failed_count=0 if column_exists else 1,
                total_count=1,
                message=(
                    "Required column exists."
                    if column_exists
                    else f"Required column is missing: {column_name}"
                ),
            )
        )

    return results
def check_not_null(
    df: pd.DataFrame,
    source_file: str,
    column_name: str,
    rule_id: str,
    severity: str,
) -> RawQualityCheckResult:
    if column_name not in df.columns:
        return build_result(
            rule_id=rule_id,
            source_file=source_file,
            column_name=column_name,
            rule_type="not_null",
            severity=severity,
            failed_count=1,
            total_count=1,
            message=f"Column not found for not-null check: {column_name}",
        )

    normalized_series = normalize_text_series(df[column_name])
    failed_count = int(normalized_series.isna().sum())
    total_count = len(df)
    return build_result(
        rule_id=rule_id,
        source_file=source_file,
        column_name=column_name,
        rule_type="not_null",
        severity=severity,
        failed_count=failed_count,
        total_count=total_count,
        message=(
            f"{column_name} has no null or blank values."
            if failed_count == 0
            else f"{column_name} contains {failed_count} null or blank values."
        ),
    )

def check_parseable_date(
    df: pd.DataFrame,
    source_file: str,
    column_name: str,
    rule_id: str,
    severity: str,
) -> RawQualityCheckResult:
    if column_name not in df.columns:
        return build_result(
            rule_id=rule_id,
            source_file=source_file,
            column_name=column_name,
            rule_type="parseable_date",
            severity=severity,
            failed_count=1,
            total_count=1,
            message=f"Column not found for parseable-date check: {column_name}",
        )

    normalized_series = normalize_text_series(df[column_name])
    non_null_values = normalized_series.dropna()
    parsed_values = pd.to_datetime(non_null_values, errors="coerce")

    failed_count = int(parsed_values.isna().sum())
    total_count = int(len(non_null_values))

    return build_result(
        rule_id=rule_id,
        source_file=source_file,
        column_name=column_name,
        rule_type="parseable_date",
        severity=severity,
        failed_count=failed_count,
        total_count=total_count,
        message=(
            f"{column_name} values are parseable as dates."
            if failed_count == 0
            else f"{column_name} contains {failed_count} non-parseable date values."
        ),
    )

def check_parseable_timestamp(
    df: pd.DataFrame,
    source_file: str,
    column_name: str,
    rule_id: str,
    severity: str,
) -> RawQualityCheckResult:
    if column_name not in df.columns:
        return build_result(
            rule_id=rule_id,
            source_file=source_file,
            column_name=column_name,
            rule_type="parseable_timestamp",
            severity=severity,
            failed_count=1,
            total_count=1,
            message=f"Column not found for parseable-timestamp check: {column_name}",
        )

    normalized_series = normalize_text_series(df[column_name])
    non_null_values = normalized_series.dropna()
    parsed_values = pd.to_datetime(non_null_values, errors="coerce")

    failed_count = int(parsed_values.isna().sum())
    total_count = int(len(non_null_values))

    return build_result(
        rule_id=rule_id,
        source_file=source_file,
        column_name=column_name,
        rule_type="parseable_timestamp",
        severity=severity,
        failed_count=failed_count,
        total_count=total_count,
        message=(
            f"{column_name} values are parseable as timestamps."
            if failed_count == 0
            else f"{column_name} contains {failed_count} non-parseable timestamp values."
        ),
    )
def check_country_code_is_br(
    df: pd.DataFrame,
    source_file: str,
) -> RawQualityCheckResult:
    column_name = "country_code"

    if column_name not in df.columns:
        return build_result(
            rule_id="BR_HOL_DQ_COUNTRY_ACCEPTED_001",
            source_file=source_file,
            column_name=column_name,
            rule_type="accepted_values",
            severity="error",
            failed_count=1,
            total_count=1,
            message="country_code column is missing.",
        )

    normalized_country = normalize_text_series(df[column_name]).str.upper()
    non_null_values = normalized_country.dropna()
    invalid_mask = non_null_values != EXPECTED_COUNTRY_CODE

    failed_count = int(invalid_mask.sum())
    total_count = int(len(non_null_values))

    return build_result(
        rule_id="BR_HOL_DQ_COUNTRY_ACCEPTED_001",
        source_file=source_file,
        column_name=column_name,
        rule_type="accepted_values",
        severity="error",
        failed_count=failed_count,
        total_count=total_count,
        message=(
            "All country_code values are BR."
            if failed_count == 0
            else f"country_code contains {failed_count} values different from BR."
        ),
    )
def check_expected_holiday_years(
    df: pd.DataFrame,
    source_file: str,
) -> RawQualityCheckResult:
    column_name = "holiday_date"

    if column_name not in df.columns:
        return build_result(
            rule_id="BR_HOL_DQ_EXPECTED_YEARS_001",
            source_file=source_file,
            column_name=column_name,
            rule_type="expected_years",
            severity="warning",
            failed_count=1,
            total_count=1,
            message="holiday_date column is missing.",
        )

    parsed_dates = pd.to_datetime(df[column_name], errors="coerce")
    actual_years = set(parsed_dates.dropna().dt.year.astype(int).unique())
    missing_years = sorted(EXPECTED_HOLIDAY_YEARS - actual_years)
    unexpected_years = sorted(actual_years - EXPECTED_HOLIDAY_YEARS)

    failed_count = len(missing_years) + len(unexpected_years)

    return build_result(
        rule_id="BR_HOL_DQ_EXPECTED_YEARS_001",
        source_file=source_file,
        column_name=column_name,
        rule_type="expected_years",
        severity="warning",
        failed_count=failed_count,
        total_count=len(EXPECTED_HOLIDAY_YEARS),
        message=(
            "Holiday dates cover expected years: 2016, 2017, 2018."
            if failed_count == 0
            else (
                "Holiday year coverage issue. "
                f"missing_years={missing_years}, unexpected_years={unexpected_years}"
            )
        ),
    )
def check_duplicate_date_name(
    df: pd.DataFrame,
    source_file: str,
) -> RawQualityCheckResult:
    key_columns = ["holiday_date", "holiday_name"]

    missing_columns = [
        column_name for column_name in key_columns if column_name not in df.columns
    ]

    if missing_columns:
        return build_result(
            rule_id="BR_HOL_DQ_DUPLICATE_DATE_NAME_001",
            source_file=source_file,
            column_name=",".join(key_columns),
            rule_type="duplicate_business_key",
            severity="warning",
            failed_count=1,
            total_count=1,
            message=(
                "Cannot check duplicate holiday date/name. "
                f"Missing columns: {missing_columns}"
            ),
        )

    key_df = df[key_columns].copy()

    for column_name in key_columns:
        key_df[column_name] = normalize_text_series(key_df[column_name])

    duplicate_count = int(key_df.duplicated(subset=key_columns, keep=False).sum())
    total_count = len(df)

    return build_result(
        rule_id="BR_HOL_DQ_DUPLICATE_DATE_NAME_001",
        source_file=source_file,
        column_name=",".join(key_columns),
        rule_type="duplicate_business_key",
        severity="warning",
        failed_count=duplicate_count,
        total_count=total_count,
        message=(
            "No duplicate holiday_date + holiday_name records found."
            if duplicate_count == 0
            else f"Found {duplicate_count} duplicate holiday_date + holiday_name rows."
        ),
    )
def check_duplicate_date_name(
    df: pd.DataFrame,
    source_file: str,
) -> RawQualityCheckResult:
    key_columns = ["holiday_date", "holiday_name"]

    missing_columns = [
        column_name for column_name in key_columns if column_name not in df.columns
    ]

    if missing_columns:
        return build_result(
            rule_id="BR_HOL_DQ_DUPLICATE_DATE_NAME_001",
            source_file=source_file,
            column_name=",".join(key_columns),
            rule_type="duplicate_business_key",
            severity="warning",
            failed_count=1,
            total_count=1,
            message=(
                "Cannot check duplicate holiday date/name. "
                f"Missing columns: {missing_columns}"
            ),
        )

    key_df = df[key_columns].copy()

    for column_name in key_columns:
        key_df[column_name] = normalize_text_series(key_df[column_name])

    duplicate_count = int(key_df.duplicated(subset=key_columns, keep=False).sum())
    total_count = len(df)

    return build_result(
        rule_id="BR_HOL_DQ_DUPLICATE_DATE_NAME_001",
        source_file=source_file,
        column_name=",".join(key_columns),
        rule_type="duplicate_business_key",
        severity="warning",
        failed_count=duplicate_count,
        total_count=total_count,
        message=(
            "No duplicate holiday_date + holiday_name records found."
            if duplicate_count == 0
            else f"Found {duplicate_count} duplicate holiday_date + holiday_name rows."
        ),
    )

def build_br_holidays_quality_checks(
    clean_data_dir: Path,
    output_dir: Path,
    run_date: str,
    source_file: str = DEFAULT_BR_HOLIDAYS_CLEAN_FILE,
) -> Path:
    logger.info(
        "Br holidays quality job started",
        extra={
            "clean_data_dir": str(clean_data_dir),
            "output_dir": str(output_dir),
            "run_date": run_date,
            "source_file": source_file,
        },
    )

    quality_results: list[RawQualityCheckResult] = []

    file_exists_result = check_clean_file_exists(
        clean_data_dir=clean_data_dir,
        run_date=run_date,
        source_file=source_file,
    )
    quality_results.append(file_exists_result)

    source_file_path = clean_data_dir / f"run_date={run_date}" / source_file

    if file_exists_result.status == "PASS":
        df = pd.read_csv(source_file_path)

        quality_results.append(
            check_file_not_empty(df=df, source_file=source_file)
        )

        quality_results.extend(
            check_required_columns(df=df, source_file=source_file)
        )

        quality_results.append(
            check_not_null(
                df=df,
                source_file=source_file,
                column_name="holiday_date",
                rule_id="BR_HOL_DQ_DATE_NOT_NULL_001",
                severity="error",
            )
        )

        quality_results.append(
            check_parseable_date(
                df=df,
                source_file=source_file,
                column_name="holiday_date",
                rule_id="BR_HOL_DQ_DATE_PARSEABLE_001",
                severity="error",
            )
        )

        quality_results.append(
            check_not_null(
                df=df,
                source_file=source_file,
                column_name="country_code",
                rule_id="BR_HOL_DQ_COUNTRY_NOT_NULL_001",
                severity="error",
            )
        )

        quality_results.append(
            check_country_code_is_br(df=df, source_file=source_file)
        )

        quality_results.append(
            check_not_null(
                df=df,
                source_file=source_file,
                column_name="holiday_name",
                rule_id="BR_HOL_DQ_NAME_NOT_NULL_001",
                severity="warning",
            )
        )

        quality_results.append(
            check_parseable_timestamp(
                df=df,
                source_file=source_file,
                column_name="extracted_at",
                rule_id="BR_HOL_DQ_EXTRACTED_AT_PARSEABLE_001",
                severity="warning",
            )
        )

        quality_results.append(
            check_parseable_date(
                df=df,
                source_file=source_file,
                column_name="run_date",
                rule_id="BR_HOL_DQ_RUN_DATE_PARSEABLE_001",
                severity="error",
            )
        )

        quality_results.append(
            check_expected_holiday_years(df=df, source_file=source_file)
        )

        quality_results.append(
            check_duplicate_date_name(df=df, source_file=source_file)
        )

    run_output_dir = output_dir / f"run_date={run_date}"
    run_output_dir.mkdir(parents=True, exist_ok=True)

    output_file = run_output_dir / "br_holidays_quality_checks.csv"

    output_columns = [
        "rule_id",
        "source_file",
        "column_name",
        "rule_type",
        "severity",
        "status",
        "failed_count",
        "total_count",
        "failure_percentage",
        "message",
        "checked_at",
    ]

    quality_df = pd.DataFrame(asdict(result) for result in quality_results)
    quality_df = quality_df[output_columns]
    quality_df.to_csv(output_file, index=False)

    failed_checks = int((quality_df["status"] == "FAIL").sum())

    logger.info(
        "Br holidays quality report written",
        extra={
            "output_file": str(output_file),
            "total_checks": len(quality_df),
            "failed_checks": failed_checks,
        },
    )

    return output_file

