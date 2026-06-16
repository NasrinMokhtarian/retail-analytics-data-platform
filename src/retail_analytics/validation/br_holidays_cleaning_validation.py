from __future__ import annotations

import logging
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import pandas as pd

from retail_analytics.models.cleaning_validation import CleaningValidationResult
from retail_analytics.config import RAW_FILE_PATTERN,BR_HOLIDAYS_CLEAN_OUTPUT_FILE
logger = logging.getLogger(__name__)



REQUIRED_COLUMNS = [
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

EXPECTED_SOURCE_FILES = {
    "br_public_holidays_2016.json",
    "br_public_holidays_2017.json",
    "br_public_holidays_2018.json",
}

EXPECTED_COUNTRY_CODE = "BR"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_result(
    check_id: str,
    source_file: str,
    cleaned_file: str,
    check_type: str,
    severity: str,
    failed_count: int,
    total_count: int,
    message: str,
    raw_row_count: int | None = None,
    cleaned_row_count: int | None = None,
) -> CleaningValidationResult:
    status = "PASS" if failed_count == 0 else "FAIL"

    return CleaningValidationResult(
        check_id=check_id,
        source_file=source_file,
        cleaned_file=cleaned_file,
        check_type=check_type,
        severity=severity,
        status=status,
        raw_row_count=raw_row_count,
        cleaned_row_count=cleaned_row_count,
        failed_count=int(failed_count),
        total_count=int(total_count),
        message=message,
        validated_at=utc_now(),
    )


def check_directory_exists(
    directory_path: Path,
    source_file: str,
    cleaned_file: str,
    check_id: str,
    check_type: str,
) -> CleaningValidationResult:
    directory_exists = directory_path.exists() and directory_path.is_dir()

    return build_result(
        check_id=check_id,
        source_file=source_file,
        cleaned_file=cleaned_file,
        check_type=check_type,
        severity="error",
        failed_count=0 if directory_exists else 1,
        total_count=1,
        message=(
            "Directory exists"
            if directory_exists
            else f"Directory is missing or not a directory: {directory_path}"
        ),
    )


def check_file_exists(
    file_path: Path,
    source_file: str,
    cleaned_file: str,
    check_id: str,
    check_type: str,
) -> CleaningValidationResult:
    file_exists = file_path.exists()

    return build_result(
        check_id=check_id,
        source_file=source_file,
        cleaned_file=cleaned_file,
        check_type=check_type,
        severity="error",
        failed_count=0 if file_exists else 1,
        total_count=1,
        message="File exists" if file_exists else f"File is missing: {file_path}",
    )


def count_raw_holiday_records(raw_run_dir: Path) -> tuple[int, int]:
    raw_files = sorted(raw_run_dir.glob(RAW_FILE_PATTERN))

    total_records = 0

    for raw_file in raw_files:
        raw_df = pd.read_json(raw_file)
        total_records += len(raw_df)

    return len(raw_files), total_records


def read_csv_safely(
    file_path: Path,
    source_file: str,
    cleaned_file: str,
) -> tuple[Optional[pd.DataFrame], CleaningValidationResult]:
    try:
        df = pd.read_csv(file_path)

        result = build_result(
            check_id="BR_HOL_CLEAN_READABLE_001",
            source_file=source_file,
            cleaned_file=cleaned_file,
            check_type="cleaned_file_readable",
            severity="error",
            failed_count=0,
            total_count=1,
            cleaned_row_count=len(df),
            message="Cleaned Brazil holidays file is readable",
        )

        return df, result

    except Exception as exc:
        result = build_result(
            check_id="BR_HOL_CLEAN_READABLE_001",
            source_file=source_file,
            cleaned_file=cleaned_file,
            check_type="cleaned_file_readable",
            severity="error",
            failed_count=1,
            total_count=1,
            message=f"Cleaned Brazil holidays file could not be read: {exc}",
        )

        return None, result


def check_raw_file_count(
    raw_run_dir: Path,
    source_file: str,
    cleaned_file: str,
) -> CleaningValidationResult:
    raw_files = sorted(raw_run_dir.glob(RAW_FILE_PATTERN))
    actual_file_names = {raw_file.name for raw_file in raw_files}

    missing_files = sorted(EXPECTED_SOURCE_FILES - actual_file_names)
    unexpected_files = sorted(actual_file_names - EXPECTED_SOURCE_FILES)

    failed_count = len(missing_files) + len(unexpected_files)

    return build_result(
        check_id="BR_HOL_RAW_FILE_SET_001",
        source_file=source_file,
        cleaned_file=cleaned_file,
        check_type="raw_file_set_matches_expected",
        severity="error",
        failed_count=failed_count,
        total_count=len(EXPECTED_SOURCE_FILES),
        message=(
            "Expected raw holiday files exist for 2016, 2017, and 2018"
            if failed_count == 0
            else (
                "Raw holiday file set does not match expected files. "
                f"missing_files={missing_files}, unexpected_files={unexpected_files}"
            )
        ),
    )


def check_row_count_matches(
    raw_row_count: int,
    cleaned_df: pd.DataFrame,
    source_file: str,
    cleaned_file: str,
) -> CleaningValidationResult:
    cleaned_row_count = len(cleaned_df)
    failed_count = 0 if raw_row_count == cleaned_row_count else 1

    return build_result(
        check_id="BR_HOL_CLEAN_ROW_COUNT_001",
        source_file=source_file,
        cleaned_file=cleaned_file,
        check_type="row_count_matches",
        severity="error",
        failed_count=failed_count,
        total_count=1,
        raw_row_count=raw_row_count,
        cleaned_row_count=cleaned_row_count,
        message=(
            "Raw and cleaned Brazil holidays row counts match"
            if failed_count == 0
            else (
                "Brazil holidays row count mismatch: "
                f"raw={raw_row_count}, cleaned={cleaned_row_count}"
            )
        ),
    )


def check_cleaned_file_not_empty(
    cleaned_df: pd.DataFrame,
    source_file: str,
    cleaned_file: str,
) -> CleaningValidationResult:
    cleaned_row_count = len(cleaned_df)
    failed_count = 0 if cleaned_row_count > 0 else 1

    return build_result(
        check_id="BR_HOL_CLEAN_NOT_EMPTY_001",
        source_file=source_file,
        cleaned_file=cleaned_file,
        check_type="cleaned_file_not_empty",
        severity="error",
        failed_count=failed_count,
        total_count=1,
        cleaned_row_count=cleaned_row_count,
        message=(
            "Cleaned Brazil holidays file is not empty"
            if failed_count == 0
            else "Cleaned Brazil holidays file is empty"
        ),
    )


def check_required_columns_exist(
    cleaned_df: pd.DataFrame,
    source_file: str,
    cleaned_file: str,
) -> CleaningValidationResult:
    actual_columns = set(cleaned_df.columns)
    missing_columns = [
        column_name
        for column_name in REQUIRED_COLUMNS
        if column_name not in actual_columns
    ]

    failed_count = len(missing_columns)

    return build_result(
        check_id="BR_HOL_CLEAN_REQUIRED_COLUMNS_001",
        source_file=source_file,
        cleaned_file=cleaned_file,
        check_type="required_columns_exist",
        severity="error",
        failed_count=failed_count,
        total_count=len(REQUIRED_COLUMNS),
        cleaned_row_count=len(cleaned_df),
        message=(
            "All required Brazil holidays cleaned columns exist"
            if failed_count == 0
            else f"Missing required columns: {missing_columns}"
        ),
    )


def check_run_date_values(
    cleaned_df: pd.DataFrame,
    source_file: str,
    cleaned_file: str,
    expected_run_date: str,
) -> CleaningValidationResult:
    column_name = "run_date"

    if column_name not in cleaned_df.columns:
        return build_result(
            check_id="BR_HOL_CLEAN_RUN_DATE_001",
            source_file=source_file,
            cleaned_file=cleaned_file,
            check_type="run_date_values_match",
            severity="error",
            failed_count=1,
            total_count=1,
            cleaned_row_count=len(cleaned_df),
            message="run_date column is missing",
        )

    invalid_count = int((cleaned_df[column_name].astype(str) != expected_run_date).sum())

    return build_result(
        check_id="BR_HOL_CLEAN_RUN_DATE_001",
        source_file=source_file,
        cleaned_file=cleaned_file,
        check_type="run_date_values_match",
        severity="error",
        failed_count=invalid_count,
        total_count=len(cleaned_df),
        cleaned_row_count=len(cleaned_df),
        message=(
            "All run_date values match expected run_date"
            if invalid_count == 0
            else f"{invalid_count} rows have unexpected run_date values"
        ),
    )


def check_country_code_values(
    cleaned_df: pd.DataFrame,
    source_file: str,
    cleaned_file: str,
) -> CleaningValidationResult:
    column_name = "country_code"

    if column_name not in cleaned_df.columns:
        return build_result(
            check_id="BR_HOL_CLEAN_COUNTRY_CODE_001",
            source_file=source_file,
            cleaned_file=cleaned_file,
            check_type="country_code_values_match",
            severity="error",
            failed_count=1,
            total_count=1,
            cleaned_row_count=len(cleaned_df),
            message="country_code column is missing",
        )

    normalized_country = cleaned_df[column_name].astype(str).str.upper().str.strip()
    invalid_count = int((normalized_country != EXPECTED_COUNTRY_CODE).sum())

    return build_result(
        check_id="BR_HOL_CLEAN_COUNTRY_CODE_001",
        source_file=source_file,
        cleaned_file=cleaned_file,
        check_type="country_code_values_match",
        severity="error",
        failed_count=invalid_count,
        total_count=len(cleaned_df),
        cleaned_row_count=len(cleaned_df),
        message=(
            "All country_code values are BR"
            if invalid_count == 0
            else f"{invalid_count} rows have country_code different from BR"
        ),
    )


def check_source_file_name_values(
    cleaned_df: pd.DataFrame,
    source_file: str,
    cleaned_file: str,
) -> CleaningValidationResult:
    column_name = "source_file_name"

    if column_name not in cleaned_df.columns:
        return build_result(
            check_id="BR_HOL_CLEAN_SOURCE_FILE_NAME_001",
            source_file=source_file,
            cleaned_file=cleaned_file,
            check_type="source_file_name_values_expected",
            severity="error",
            failed_count=1,
            total_count=1,
            cleaned_row_count=len(cleaned_df),
            message="source_file_name column is missing",
        )

    source_files = set(cleaned_df[column_name].dropna().astype(str).unique())

    missing_files = sorted(EXPECTED_SOURCE_FILES - source_files)
    unexpected_files = sorted(source_files - EXPECTED_SOURCE_FILES)

    failed_count = len(missing_files) + len(unexpected_files)

    return build_result(
        check_id="BR_HOL_CLEAN_SOURCE_FILE_NAME_001",
        source_file=source_file,
        cleaned_file=cleaned_file,
        check_type="source_file_name_values_expected",
        severity="error",
        failed_count=failed_count,
        total_count=len(EXPECTED_SOURCE_FILES),
        cleaned_row_count=len(cleaned_df),
        message=(
            "Cleaned source_file_name values match expected raw files"
            if failed_count == 0
            else (
                "Unexpected source_file_name values. "
                f"missing_files={missing_files}, unexpected_files={unexpected_files}"
            )
        ),
    )


def check_required_fields_not_null(
    cleaned_df: pd.DataFrame,
    source_file: str,
    cleaned_file: str,
) -> CleaningValidationResult:
    required_fields = ["holiday_date", "holiday_name", "country_code", "run_date"]
    missing_columns = [
        column_name
        for column_name in required_fields
        if column_name not in cleaned_df.columns
    ]

    if missing_columns:
        return build_result(
            check_id="BR_HOL_CLEAN_REQUIRED_FIELDS_NOT_NULL_001",
            source_file=source_file,
            cleaned_file=cleaned_file,
            check_type="required_fields_not_null",
            severity="error",
            failed_count=len(missing_columns),
            total_count=len(required_fields),
            cleaned_row_count=len(cleaned_df),
            message=f"Cannot check required fields. Missing columns: {missing_columns}",
        )

    failed_count = 0

    for column_name in required_fields:
        normalized_values = cleaned_df[column_name].astype("string").str.strip()
        failed_count += int(normalized_values.isna().sum())
        failed_count += int((normalized_values == "").sum())

    total_count = len(cleaned_df) * len(required_fields)

    return build_result(
        check_id="BR_HOL_CLEAN_REQUIRED_FIELDS_NOT_NULL_001",
        source_file=source_file,
        cleaned_file=cleaned_file,
        check_type="required_fields_not_null",
        severity="error",
        failed_count=failed_count,
        total_count=total_count,
        cleaned_row_count=len(cleaned_df),
        message=(
            "Required Brazil holidays fields have no null or blank values"
            if failed_count == 0
            else f"{failed_count} required field values are null or blank"
        ),
    )


def check_date_fields_parseable(
    cleaned_df: pd.DataFrame,
    source_file: str,
    cleaned_file: str,
) -> CleaningValidationResult:
    date_fields = ["holiday_date", "run_date"]
    missing_columns = [
        column_name
        for column_name in date_fields
        if column_name not in cleaned_df.columns
    ]

    if missing_columns:
        return build_result(
            check_id="BR_HOL_CLEAN_DATE_FIELDS_PARSEABLE_001",
            source_file=source_file,
            cleaned_file=cleaned_file,
            check_type="date_fields_parseable",
            severity="error",
            failed_count=len(missing_columns),
            total_count=len(date_fields),
            cleaned_row_count=len(cleaned_df),
            message=f"Cannot check date fields. Missing columns: {missing_columns}",
        )

    failed_count = 0
    total_count = 0

    for column_name in date_fields:
        values = cleaned_df[column_name].dropna().astype(str).str.strip()
        parsed_values = pd.to_datetime(values, errors="coerce")
        failed_count += int(parsed_values.isna().sum())
        total_count += len(values)

    return build_result(
        check_id="BR_HOL_CLEAN_DATE_FIELDS_PARSEABLE_001",
        source_file=source_file,
        cleaned_file=cleaned_file,
        check_type="date_fields_parseable",
        severity="error",
        failed_count=failed_count,
        total_count=total_count,
        cleaned_row_count=len(cleaned_df),
        message=(
            "Date fields are parseable"
            if failed_count == 0
            else f"{failed_count} date field values are not parseable"
        ),
    )


def check_extracted_at_parseable(
    cleaned_df: pd.DataFrame,
    source_file: str,
    cleaned_file: str,
) -> CleaningValidationResult:
    column_name = "extracted_at"

    if column_name not in cleaned_df.columns:
        return build_result(
            check_id="BR_HOL_CLEAN_EXTRACTED_AT_PARSEABLE_001",
            source_file=source_file,
            cleaned_file=cleaned_file,
            check_type="extracted_at_parseable",
            severity="warning",
            failed_count=1,
            total_count=1,
            cleaned_row_count=len(cleaned_df),
            message="extracted_at column is missing",
        )

    values = cleaned_df[column_name].dropna().astype(str).str.strip()
    parsed_values = pd.to_datetime(values, errors="coerce")
    failed_count = int(parsed_values.isna().sum())

    return build_result(
        check_id="BR_HOL_CLEAN_EXTRACTED_AT_PARSEABLE_001",
        source_file=source_file,
        cleaned_file=cleaned_file,
        check_type="extracted_at_parseable",
        severity="warning",
        failed_count=failed_count,
        total_count=len(values),
        cleaned_row_count=len(cleaned_df),
        message=(
            "extracted_at values are parseable"
            if failed_count == 0
            else f"{failed_count} extracted_at values are not parseable"
        ),
    )


def validate_br_holidays_cleaned_output(
    raw_data_dir: Path,
    cleaned_data_dir: Path,
    output_dir: Path,
    run_date: str,
    source_file: str = "br_public_holidays_*.json",
    cleaned_file: str = BR_HOLIDAYS_CLEAN_OUTPUT_FILE,
) -> Path:
    raw_run_dir = raw_data_dir / f"run_date={run_date}"
    cleaned_file_path = cleaned_data_dir / f"run_date={run_date}" / cleaned_file
    run_output_dir = output_dir / f"run_date={run_date}"
    run_output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(
        "Brazil holidays cleaned output validation started",
        extra={
            "raw_run_dir": str(raw_run_dir),
            "cleaned_file_path": str(cleaned_file_path),
            "output_dir": str(run_output_dir),
            "run_date": run_date,
        },
    )

    validation_results: list[CleaningValidationResult] = []

    raw_dir_result = check_directory_exists(
        directory_path=raw_run_dir,
        source_file=source_file,
        cleaned_file=cleaned_file,
        check_id="BR_HOL_RAW_DIR_EXISTS_001",
        check_type="raw_run_directory_exists",
    )
    validation_results.append(raw_dir_result)

    cleaned_exists_result = check_file_exists(
        file_path=cleaned_file_path,
        source_file=source_file,
        cleaned_file=cleaned_file,
        check_id="BR_HOL_CLEAN_EXISTS_001",
        check_type="cleaned_file_exists",
    )
    validation_results.append(cleaned_exists_result)

    if raw_dir_result.status == "FAIL" or cleaned_exists_result.status == "FAIL":
        logger.warning(
            "Skipping deeper Brazil holidays validation because raw directory or cleaned file is missing",
            extra={
                "raw_run_dir": str(raw_run_dir),
                "cleaned_file_path": str(cleaned_file_path),
            },
        )
    else:
        validation_results.append(
            check_raw_file_count(
                raw_run_dir=raw_run_dir,
                source_file=source_file,
                cleaned_file=cleaned_file,
            )
        )

        raw_file_count, raw_row_count = count_raw_holiday_records(raw_run_dir)

        cleaned_df, readable_result = read_csv_safely(
            file_path=cleaned_file_path,
            source_file=source_file,
            cleaned_file=cleaned_file,
        )
        validation_results.append(readable_result)

        if cleaned_df is not None:
            validation_results.append(
                check_row_count_matches(
                    raw_row_count=raw_row_count,
                    cleaned_df=cleaned_df,
                    source_file=source_file,
                    cleaned_file=cleaned_file,
                )
            )

            validation_results.append(
                check_cleaned_file_not_empty(
                    cleaned_df=cleaned_df,
                    source_file=source_file,
                    cleaned_file=cleaned_file,
                )
            )

            validation_results.append(
                check_required_columns_exist(
                    cleaned_df=cleaned_df,
                    source_file=source_file,
                    cleaned_file=cleaned_file,
                )
            )

            validation_results.append(
                check_run_date_values(
                    cleaned_df=cleaned_df,
                    source_file=source_file,
                    cleaned_file=cleaned_file,
                    expected_run_date=run_date,
                )
            )

            validation_results.append(
                check_country_code_values(
                    cleaned_df=cleaned_df,
                    source_file=source_file,
                    cleaned_file=cleaned_file,
                )
            )

            validation_results.append(
                check_source_file_name_values(
                    cleaned_df=cleaned_df,
                    source_file=source_file,
                    cleaned_file=cleaned_file,
                )
            )

            validation_results.append(
                check_required_fields_not_null(
                    cleaned_df=cleaned_df,
                    source_file=source_file,
                    cleaned_file=cleaned_file,
                )
            )

            validation_results.append(
                check_date_fields_parseable(
                    cleaned_df=cleaned_df,
                    source_file=source_file,
                    cleaned_file=cleaned_file,
                )
            )

            validation_results.append(
                check_extracted_at_parseable(
                    cleaned_df=cleaned_df,
                    source_file=source_file,
                    cleaned_file=cleaned_file,
                )
            )

    output_file = run_output_dir / "br_holidays_cleaning_validation_report.csv"

    output_columns = [
        "check_id",
        "source_file",
        "cleaned_file",
        "check_type",
        "severity",
        "status",
        "raw_row_count",
        "cleaned_row_count",
        "failed_count",
        "total_count",
        "message",
        "validated_at",
    ]

    validation_df = pd.DataFrame(asdict(result) for result in validation_results)
    validation_df = validation_df[output_columns]
    validation_df.to_csv(output_file, index=False)

    failed_checks = int((validation_df["status"] == "FAIL").sum())

    logger.info(
        "Brazil holidays cleaned output validation completed",
        extra={
            "output_file": str(output_file),
            "total_checks": len(validation_df),
            "failed_checks": failed_checks,
        },
    )

    return output_file