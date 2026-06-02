import logging
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd # type: ignore[import]
from retail_analytics.models.raw_quality import RawQualityCheckResult
from retail_analytics.validation.raw_files import validate_row_data_dir

logger = logging.getLogger(__name__)


EXPECTED_SUPPLIER_FILE: dict[str,list[str]] = {
    "supplier_product_updates_2026-05-24.csv" :[
        "supplier_id",
        "product_id",
        "supplier_product_code",
        "updated_price",
        "currency",
        "stock_status",
        "valid_from",
        "last_updated_at",
        "comments",
        ]
    }

DEFAULT_SUPPLIER_SOURCE_FILE = "supplier_product_updates_2026-05-24.csv"

NOT_NULL_RULES: list[tuple[str,str,str]] = [
    ("SUP_DQ_NOT_NULL_DQ001", "supplier_id", "error"),
    ("SUP_DQ_NOT_NULL_DQ002", "supplier_name", "error"),
    ("SUP_DQ_NOT_NULL_DQ003", "product_id", "warning"),
    ("SUP_DQ_NOT_NULL_DQ004", "supplier_product_code", "error"),
    ("SUP_DQ_NOT_NULL_DQ005", "updated_price", "error"),
    ("SUP_DQ_NOT_NULL_DQ006", "updated_price", "error"),
    ("SUP_DQ_NOT_NULL_DQ007", "currency", "error"),
    ("SUP_DQ_NOT_NULL_DQ008", "valid_from", "warning"),
    ("SUP_DQ_NOT_NULL_DQ009", "last_updated_at", "warning"),
]

ALLOWED_CURRENCIES: set[str] = {"USD", "EUR"}
ALLOWED_STOCK_STATUS: set[str] = {"IN_STOCK", "OUT_OF_STOCK", "LIMITED","DISCONTINUED"}

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
def calculate_failure_percentage(failed_count:int, total_count:int) -> float:
    return round((failed_count / total_count)*100, 2)

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
    status ="PASS" if failed_count == 0 else "FAIL"

    return RawQualityCheckResult(
        rule_id=rule_id,
        source_file=source_file,
        column_name=column_name,
        rule_type=rule_type,
        severity=severity,
        status=status,
        failed_count=failed_count,
        total_count=total_count,
        failure_percentage = calculate_failure_percentage(failed_count, total_count),
        message=message,
        checked_at = utc_now()
    )

def normalize_text_series(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().replace('', pd.NA)

def normalize_price_series(series:pd.Series) -> pd.Series:
    """
        Normalize supplier price values before numeric validation.

        Handles:
        - leading/trailing spaces
        - comma decimal separator, e.g. 120,50
    """
    return series.astype(str).str.strip().str.replace(',','.',regex = False).replace('', pd.NA)

def normalize_stock_status_series(series:pd.Series) -> pd.Series:
    """
        Normalize stock status values to a controlled format.

        Examples:
        - "In Stock" -> "IN_STOCK"
        - "in stock" -> "IN_STOCK"
        - "Out of Stock" -> "OUT_OF_STOCK"
    """
    return series.astype(str).str.strip().str.upper().str.replace(' ','_',regex = False).replace('', pd.NA)

def normalize_currency_series(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().str.upper().replace('', pd.NA)

def check_expected_file_exists(raw_data_dir: Path, source_file: str) -> RawQualityCheckResult:
    file_path = raw_data_dir / source_file
    file_exists = file_path.exists()
    return build_result(
        rule_id = "SUP_DQ_FILE_EXIXTS_001",
        source_file = source_file,
        column_name = None,
        rule_type = "file_exists",
        severity = 'error',
        failed_count = 0 if file_exists else 1,
        total_count =1,
        message = ("Expected supplier file exists." if file_exists else f"Expected supplier file is missing {source_file}")
    )

def check_required_columns (df: pd.DataFrame, source_file: str) -> list[RawQualityCheckResult]:
    results: list[RawQualityCheckResult] = []
    actual_columns = set(df.columns)
    for column_name in EXPECTED_SUPPLIER_FILE[source_file]:
        column_exists = column_name in actual_columns
        results.append(
                build_result(
                    rule_id = f"SUP_DQ_REQUIRED_COLUMN_{column_name}",
                    source_file = source_file,
                    column_name = column_name,
                    rule_type = "required_column_exists",
                    severity = "error",
                    failed_count = 0 if column_exists else 1,
                    total_count = 1,
                    message = "Required column exists" if column_exists else f"Required column is missing: {column_name}")
                    )
    return results

def check_not_null(df: pd.DataFrame, source_file: str, column_name: str, rule_id: str, severity: str) -> RawQualityCheckResult:
    if column_name not in df.columns:
        return build_result(
            rule_id = rule_id,
            source_file = source_file,
            column_name = column_name,
            rule_type = "not_null",
            severity = severity,
            failed_count = 1,
            total_count = 1,
            message = f"Column not found for not_null_check:{column_name} "
        )
    normalize_series = normalize_text_series(df[column_name])
    failed_count = int(normalize_series.isna().sum())
    total_count = len(df)
    return build_result(
        rule_id = rule_id,
        source_file = source_file,
        column_name = column_name,
        rule_type = "not_null",
        severity = severity,
        failed_count = failed_count,
        total_count = total_count,
        message =  f"Column has no null values" if failed_count ==0 else f"Column containes {failed_count} null or blank values"
    )
def check_price_parsable_numeric(df: pd.DataFrame,source_file:str) -> RawQualityCheckResult:
    column_name = "updated_price"
    if column_name not in df.columns:
        return build_result(
            rule_id = "SUP_DQ_PRICE_NUMERIC_001",
            source_file = source_file,
            column_name = column_name,
            rule_type = "parseable_numeric",
            severity = "error",
            failed_count = 1,
            total_count = 1,
            message = f"updated_price column is missing"
        )
    normalized_price = normalize_price_series(df[column_name])
    numeric_price = pd.to_numeric(normalized_price, errors='coerce')
    invalid_mask = numeric_price.isna() & normalized_price.notna()
    failed_count = int(invalid_mask.sum())
    total_count = int(normalized_price.notna().sum())

    return build_result(
        rule_id="SUP_DQ_PRICE_NUMERIC_001",
        source_file=source_file,
        column_name=column_name,
        rule_type="parseable_numeric",
        severity="error",
        failed_count=failed_count,
        total_count=total_count,
        message=f"updated_price values are parseable as numeric" if failed_count == 0 else f"updated_price contains {failed_count} non-parseable values"
    )

def check_price_non_negative(df: pd.DataFrame, source_file: str) -> RawQualityCheckResult:
    column_name = "updated_price"
    if column_name not in df.columns:
        return build_result(
            rule_id = "SUP_DQ_PRICE_NON_NEGATIVE_001",
            source_file = source_file,
            column_name = column_name,
            rule_type = "non_negative",
            severity = "error",
            failed_count = 1,
            total_count = 1,
            message = f"updated_price column is missing"
        )
    normalized_price = normalize_price_series(df[column_name])
    numeric_price = pd.to_numeric(normalized_price, errors='coerce')
    negative_mask = (numeric_price < 0) 
    failed_count = int(negative_mask.sum())
    total_count = int(numeric_price.notna().sum())

    return build_result(
        rule_id="SUP_DQ_PRICE_NON_NEGATIVE_001",
        source_file=source_file,
        column_name=column_name,
        rule_type="non_negative",
        severity="error",
        failed_count=failed_count,
        total_count=total_count,
        message=f"updated_price values are non-negative" if failed_count == 0 else f"updated_price contains {failed_count} negative values"
    )

def check_currency_accepted_values(
    df: pd.DataFrame,
    source_file: str,
) -> RawQualityCheckResult:
    column_name = "currency"

    if column_name not in df.columns:
        return build_result(
            rule_id="SUP_DQ_CURRENCY_ACCEPTED_001",
            source_file=source_file,
            column_name=column_name,
            rule_type="accepted_values",
            severity="error",
            failed_count=1,
            total_count=1,
            message="currency column is missing",
        )

    normalized_currency = normalize_currency_series(df[column_name])
    non_null_values = normalized_currency.dropna()

    invalid_mask = ~non_null_values.isin(ALLOWED_CURRENCIES)
    failed_count = int(invalid_mask.sum())
    total_count = int(len(non_null_values))

    return build_result(
        rule_id="SUP_DQ_CURRENCY_ACCEPTED_001",
        source_file=source_file,
        column_name=column_name,
        rule_type="accepted_values",
        severity="error",
        failed_count=failed_count,
        total_count=total_count,
        message=(
            "currency values are within accepted values"
            if failed_count == 0
            else f"currency contains {failed_count} values outside accepted values"
        ),
    )


def check_stock_status_accepted_values(
    df: pd.DataFrame,
    source_file: str,
) -> RawQualityCheckResult:
    column_name = "stock_status"

    if column_name not in df.columns:
        return build_result(
            rule_id="SUP_DQ_STOCK_STATUS_ACCEPTED_001",
            source_file=source_file,
            column_name=column_name,
            rule_type="accepted_values",
            severity="warning",
            failed_count=1,
            total_count=1,
            message="stock_status column is missing",
        )

    normalized_status = normalize_stock_status_series(df[column_name])
    non_null_values = normalized_status.dropna()

    invalid_mask = ~non_null_values.isin(ALLOWED_STOCK_STATUS)
    failed_count = int(invalid_mask.sum())
    total_count = int(len(non_null_values))

    return build_result(
        rule_id="SUP_DQ_STOCK_STATUS_ACCEPTED_001",
        source_file=source_file,
        column_name=column_name,
        rule_type="accepted_values",
        severity="warning",
        failed_count=failed_count,
        total_count=total_count,
        message=(
            "stock_status values are within accepted values"
            if failed_count == 0
            else f"stock_status contains {failed_count} values outside accepted values"
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
            message=f"{column_name} column is missing",
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
            f"{column_name} values are parseable"
            if failed_count == 0
            else f"{column_name} contains {failed_count} non-parseable values"
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
            message=f"{column_name} column is missing",
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
            f"{column_name} values are parseable"
            if failed_count == 0
            else f"{column_name} contains {failed_count} non-parseable values"
        ),
    )


def check_duplicate_business_key(
    df: pd.DataFrame,
    source_file: str,
) -> RawQualityCheckResult:
    key_columns = ["supplier_id", "product_id", "supplier_product_code"]

    missing_key_columns = [
        column_name for column_name in key_columns if column_name not in df.columns
    ]

    if missing_key_columns:
        return build_result(
            rule_id="SUP_DQ_DUPLICATE_KEY_001",
            source_file=source_file,
            column_name=",".join(key_columns),
            rule_type="duplicate_business_key",
            severity="warning",
            failed_count=1,
            total_count=1,
            message=f"Cannot check duplicate business key. Missing columns: {missing_key_columns}",
        )

    key_df = df[key_columns].copy()

    for column_name in key_columns:
        key_df[column_name] = normalize_text_series(key_df[column_name])

    duplicate_count = int(key_df.duplicated(subset=key_columns, keep=False).sum())
    total_count = len(df)

    return build_result(
        rule_id="SUP_DQ_DUPLICATE_KEY_001",
        source_file=source_file,
        column_name=",".join(key_columns),
        rule_type="duplicate_business_key",
        severity="warning",
        failed_count=duplicate_count,
        total_count=total_count,
        message=(
            "No duplicate supplier business keys found"
            if duplicate_count == 0
            else f"Found {duplicate_count} rows with duplicate supplier business keys"
        ),
    )


def build_supplier_quality_checks(
    raw_data_dir: Path,
    output_dir: Path,
    run_date: str,
    source_file: str = DEFAULT_SUPPLIER_SOURCE_FILE,
) -> Path:
    validate_row_data_dir(raw_data_dir)

    logger.info(
        "Supplier quality job started",
        extra={
            "raw_data_dir": str(raw_data_dir),
            "output_dir": str(output_dir),
            "run_date": run_date,
            "source_file": source_file,
        },
    )

    quality_results: list[RawQualityCheckResult] = []

    file_exists_result = check_expected_file_exists(
        raw_data_dir=raw_data_dir,
        source_file=source_file,
    )
    quality_results.append(file_exists_result)

    source_file_path = raw_data_dir / source_file

    if file_exists_result.status == "PASS":
        df = pd.read_csv(source_file_path)

        quality_results.extend(
            check_required_columns(
                df=df,
                source_file=source_file,
            )
        )

        for rule_id, column_name, severity in NOT_NULL_RULES:
            quality_results.append(
                check_not_null(
                    df=df,
                    source_file=source_file,
                    column_name=column_name,
                    rule_id=rule_id,
                    severity=severity,
                )
            )

        quality_results.append(
            check_price_parsable_numeric(
                df=df,
                source_file=source_file,
            )
        )

        quality_results.append(
            check_price_non_negative(
                df=df,
                source_file=source_file,
            )
        )

        quality_results.append(
            check_currency_accepted_values(
                df=df,
                source_file=source_file,
            )
        )

        quality_results.append(
            check_stock_status_accepted_values(
                df=df,
                source_file=source_file,
            )
        )

        quality_results.append(
            check_parseable_date(
                df=df,
                source_file=source_file,
                column_name="valid_from",
                rule_id="SUP_DQ_VALID_FROM_DATE_001",
                severity="warning",
            )
        )

        quality_results.append(
            check_parseable_timestamp(
                df=df,
                source_file=source_file,
                column_name="last_updated_at",
                rule_id="SUP_DQ_LAST_UPDATED_TIMESTAMP_001",
                severity="warning",
            )
        )

        quality_results.append(
            check_duplicate_business_key(
                df=df,
                source_file=source_file,
            )
        )

    run_output_dir = output_dir / f"run_date={run_date}"
    run_output_dir.mkdir(parents=True, exist_ok=True)

    output_file = run_output_dir / "supplier_quality_checks.csv"

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
        "Supplier quality report written",
        extra={
            "output_file": str(output_file),
            "total_checks": len(quality_df),
            "failed_checks": failed_checks,
        },
    )

    return output_file
