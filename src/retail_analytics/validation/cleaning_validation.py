import logging
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd # type: ignore [import]

from retail_analytics.cleaning.olist_rules import OLIST_OUTPUT_FILE_NAMES
from retail_analytics.models.cleaning_validation import CleaningValidationResult
from retail_analytics.validation.raw_files import validate_row_data_dir


logger = logging.getLogger(__name__)

REQUIRED_METADATA_COLUMNS = [
    "source_file_name",
    "ingested_at",
    "run_date",
]

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def calculate_status(failed_count: int) -> str:
    return "PASS" if failed_count == 0 else "FAIL"

def build_result (
    check_id: str,
    source_file: str,
    cleaned_file: str,
    check_type: str,
    severity: str,
    failed_count: int,
    total_count: int,
    message: str,
    raw_row_count: int | None = None,
    cleaned_row_count: int | None = None
    
    ) -> CleaningValidationResult:
        
    return CleaningValidationResult(
        check_id=check_id,
        source_file=source_file,
        cleaned_file=cleaned_file,
        check_type=check_type,
        severity=severity,
        status=calculate_status(failed_count),
        raw_row_count=raw_row_count,
        cleaned_row_count=cleaned_row_count,
        failed_count=failed_count,
        total_count=int(total_count),
        message=message,
        validated_at=utc_now()
        )

def check_file_exists(file_path: Path, source_file: str, cleaned_file: str,check_id:str, check_type: str) -> CleaningValidationResult:
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

def read_csv_safely(file_path: Path,source_file: str,cleaned_file: str) -> tuple[pd.DataFrame | None, CleaningValidationResult]:
    try:
        df = pd.read_csv(file_path)
        result = build_result(
            check_id=f"DQ_CLEAN_READABLE_{cleaned_file}",
            source_file=source_file,
            cleaned_file=cleaned_file,
            check_type="cleaned_file_readable",
            severity="error",
            failed_count=0,
            total_count=1,
            message="clean file is readable",
        )
        return df, result
    except Exception as e:
        logger.error(f"error reading cleaned file {cleaned_file}: {e}")
        result = build_result(
            check_id=f"DQ_CLEAN_READABLE_{cleaned_file}",
            source_file=source_file,
            cleaned_file=cleaned_file,
            check_type="cleaned_file_readable",
            severity="error",
            failed_count=1,
            total_count=1,
            message=f"Cleaned file could not be read: {e}",
        )
        return None, result
def check_row_count_matches(raw_df: pd.DataFrame,cleaned_df: pd.DataFrame,source_file: str,cleaned_file: str) -> CleaningValidationResult:
    raw_row_count =len(raw_df)
    cleaned_row_count = len(cleaned_df)
    failed_count = 0 if raw_row_count == cleaned_row_count else 1
    result =  build_result(
        check_id = f"DO_CLEAN_ROW_COUNT_{cleaned_file}",
        source_file=source_file,
        cleaned_file=cleaned_file,
        check_type="row_count_matches",
        severity="error",
        failed_count=failed_count,
        total_count=1,
        message=f"Row count mismatch: raw= {raw_row_count}, cleaned = {cleaned_row_count}",
    )
    return result

def cleaned_row_count_not_empty (cleaned_df : pd.DataFrame, source_file: str, cleaned_file: str) -> CleaningValidationResult:
    cleaned_row_count = len(cleaned_df)
    failed_count = 0 if cleaned_row_count > 0 else 1

    return build_result(
        check_id=f"DQ_CLEAN_NOT_EMPTY_{cleaned_file}",
        source_file=source_file,
        cleaned_file=cleaned_file,
        check_type="cleaned_file_not_empty",
        severity="error",
        failed_count=failed_count,
        total_count=1,
        cleaned_row_count=cleaned_row_count,
        message=(
            "Cleaned file is not empty"
            if failed_count == 0
            else "Cleaned file is empty"
        ),
    )
def check_metadata_columns_exist(cleaned_df: pd.DataFrame,source_file: str,cleaned_file: str) -> CleaningValidationResult:
    actual_columns = set(cleaned_df.columns)
    missing_columns = [
        column_name
        for column_name in REQUIRED_METADATA_COLUMNS
        if column_name not in actual_columns
    ]

    failed_count = len(missing_columns)

    return build_result(
        check_id=f"DQ_CLEAN_METADATA_COLUMNS_{cleaned_file}",
        source_file=source_file,
        cleaned_file=cleaned_file,
        check_type="metadata_columns_exist",
        severity="error",
        failed_count=failed_count,
        total_count=len(REQUIRED_METADATA_COLUMNS),
        cleaned_row_count=len(cleaned_df),
        message=(
            "All required metadata columns exist"
            if failed_count == 0
            else f"Missing metadata columns: {missing_columns}"
        ),
    )


def check_run_date_values(cleaned_df: pd.DataFrame,source_file: str,cleaned_file: str,expected_run_date: str) -> CleaningValidationResult:
    
    if "run_date" not in cleaned_df.columns:
        return build_result(
            check_id=f"DQ_CLEAN_RUN_DATE_VALUES_{cleaned_file}",
            source_file=source_file,
            cleaned_file=cleaned_file,
            check_type="run_date_values_match",
            severity="error",
            failed_count=1,
            total_count=1,
            cleaned_row_count=len(cleaned_df),
            message="run_date column is missing",
        )

    invalid_count = int((cleaned_df["run_date"].astype(str) != expected_run_date).sum())
    total_count = len(cleaned_df)

    return build_result(
        check_id=f"DQ_CLEAN_RUN_DATE_VALUES_{cleaned_file}",
        source_file=source_file,
        cleaned_file=cleaned_file,
        check_type="run_date_values_match",
        severity="error",
        failed_count=invalid_count,
        total_count=total_count,
        cleaned_row_count=total_count,
        message=(
            "All run_date values match expected run_date"
            if invalid_count == 0
            else f"{invalid_count} rows have unexpected run_date values"
        ),
    )


def check_source_file_name_values(
    cleaned_df: pd.DataFrame,
    source_file: str,
    cleaned_file: str,
) -> CleaningValidationResult:
    if "source_file_name" not in cleaned_df.columns:
        return build_result(
            check_id=f"DQ_CLEAN_SOURCE_FILE_VALUES_{cleaned_file}",
            source_file=source_file,
            cleaned_file=cleaned_file,
            check_type="source_file_name_values_match",
            severity="error",
            failed_count=1,
            total_count=1,
            cleaned_row_count=len(cleaned_df),
            message="source_file_name column is missing",
        )

    invalid_count = int((cleaned_df["source_file_name"].astype(str) != source_file).sum())
    total_count = len(cleaned_df)

    return build_result(
        check_id=f"DQ_CLEAN_SOURCE_FILE_VALUES_{cleaned_file}",
        source_file=source_file,
        cleaned_file=cleaned_file,
        check_type="source_file_name_values_match",
        severity="error",
        failed_count=invalid_count,
        total_count=total_count,
        cleaned_row_count=total_count,
        message=(
            "All source_file_name values match expected source file"
            if invalid_count == 0
            else f"{invalid_count} rows have unexpected source_file_name values"
        ),
    )


def validate_cleaned_outputs(
    raw_data_dir: Path,
    cleaned_data_dir: Path,
    output_dir: Path,
    run_date: str,
) -> Path:
    validate_row_data_dir(raw_data_dir)

    cleaned_run_dir = cleaned_data_dir / f"run_date={run_date}"
    run_output_dir = output_dir / f"run_date={run_date}"
    run_output_dir.mkdir(parents=True, exist_ok=True)

    validation_results: list[CleaningValidationResult] = []

    logger.info(
        "Cleaned output validation started",
        extra={
            "raw_data_dir": str(raw_data_dir),
            "cleaned_run_dir": str(cleaned_run_dir),
            "output_dir": str(run_output_dir),
            "run_date": run_date,
        },
    )

    for source_file, cleaned_file in OLIST_OUTPUT_FILE_NAMES.items():
        raw_file_path = raw_data_dir / source_file
        cleaned_file_path = cleaned_run_dir / cleaned_file

        logger.info(
            "Validating cleaned file",
            extra={
                "source_file": source_file,
                "cleaned_file": cleaned_file,
                "raw_file_path": str(raw_file_path),
                "cleaned_file_path": str(cleaned_file_path),
            },
        )

        raw_exists_result = check_file_exists(
            file_path=raw_file_path,
            source_file=source_file,
            cleaned_file=cleaned_file,
            check_id=f"DQ_RAW_EXISTS_{source_file}",
            check_type="raw_file_exists",
        )
        validation_results.append(raw_exists_result)

        cleaned_exists_result = check_file_exists(
            file_path=cleaned_file_path,
            source_file=source_file,
            cleaned_file=cleaned_file,
            check_id=f"DQ_CLEAN_EXISTS_{cleaned_file}",
            check_type="cleaned_file_exists",
        )
        validation_results.append(cleaned_exists_result)

        if raw_exists_result.status == "FAIL" or cleaned_exists_result.status == "FAIL":
            logger.warning(
                "Skipping deeper validation because raw or cleaned file is missing",
                extra={
                    "source_file": source_file,
                    "cleaned_file": cleaned_file,
                },
            )
            continue

        raw_df = pd.read_csv(raw_file_path)
        cleaned_df, readable_result = read_csv_safely(
            file_path=cleaned_file_path,
            source_file=source_file,
            cleaned_file=cleaned_file,
        )
        validation_results.append(readable_result)

        if cleaned_df is None:
            continue

        validation_results.append(
            check_row_count_matches(
                raw_df=raw_df,
                cleaned_df=cleaned_df,
                source_file=source_file,
                cleaned_file=cleaned_file,
            )
        )

        validation_results.append(
            cleaned_row_count_not_empty(
                cleaned_df=cleaned_df,
                source_file=source_file,
                cleaned_file=cleaned_file,
            )
        )

        validation_results.append(
            check_metadata_columns_exist(
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
            check_source_file_name_values(
                cleaned_df=cleaned_df,
                source_file=source_file,
                cleaned_file=cleaned_file,
            )
        )

    output_file = run_output_dir / "cleaning_validation_report.csv"

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
        "Cleaned output validation completed",
        extra={
            "output_file": str(output_file),
            "total_checks": len(validation_df),
            "failed_checks": failed_checks,
        },
    )

    return output_file