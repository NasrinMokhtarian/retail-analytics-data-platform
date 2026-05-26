import logging
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd # type: ignore[import]

from retail_analytics.models.raw_quality import RawQualityCheckResult
from retail_analytics.validation.raw_files import validate_row_data_dir

logger = logging.getLogger(__name__)

EXPECTED_OLIST_FILES : dict[str,list[str]] = {
    "olist_customers_dataset.csv" :[
        "customer_id",
        "customer_unique_id",
        "customer_zip_code_prefix",
        "customer_city",
        "customer_state",
    ],
    "olist_geolocation_dataset.csv": [
        "geolocation_zip_code_prefix",
        "geolocation_lat",
        "geolocation_lng",
        "geolocation_city",
        "geolocation_state",

    ],
    "olist_order_items_dataset.csv": [
        "order_id",
        "order_item_id",
        "product_id",
        "seller_id",
        "shipping_limit_date",
        "price",
        "freight_value",
    ],
    "olist_order_reviews_dataset.csv": [
        "review_id",
        "order_id",
        "review_score",
        "review_comment_title",
        "review_comment_message",
        "review_creation_date",
        "review_answer_timestamp",
    ],
    "olist_orders_dataset.csv": [
        "order_id",
        "customer_id",
        "order_status",
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
    "olist_products_dataset.csv": [
        "product_id",
        "product_category_name",
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    ],
    "olist_sellers_dataset.csv": [
        "seller_id",
        "seller_zip_code_prefix",
        "seller_city",
        "seller_state",
    ],
    "product_category_name_translation.csv": [
        "product_category_name",
        "product_category_name_english",
    ],
}

NOT_NULL_RULES: list[tuple[str,str,str,str]] = [
    ("DQ_NOT_NULL_001", "olist_orders_dataset.csv", "order_id", "error"),
    ("DQ_NOT_NULL_002", "olist_orders_dataset.csv", "customer_id", "error"),
    ("DQ_NOT_NULL_003", "olist_customers_dataset.csv", "customer_id", "error"),
    ("DQ_NOT_NULL_004", "olist_order_items_dataset.csv", "order_id", "error"),
    ("DQ_NOT_NULL_005", "olist_order_items_dataset.csv", "product_id", "error"),
    ("DQ_NOT_NULL_006", "olist_order_items_dataset.csv", "seller_id", "error"),
    ("DQ_NOT_NULL_007", "olist_order_payments_dataset.csv", "order_id", "error"),
    ("DQ_NOT_NULL_008", "olist_order_reviews_dataset.csv", "review_id", "error"),
    ("DQ_NOT_NULL_009", "olist_order_reviews_dataset.csv", "order_id", "error"),
    ("DQ_NOT_NULL_010", "olist_products_dataset.csv", "product_id", "error"),
    ("DQ_NOT_NULL_011", "olist_sellers_dataset.csv", "seller_id", "error"),

]
NON_NEGATIVE_RULES: list[tuple[str, str, str, str]] = [
    ("DQ_NON_NEG_001", "olist_order_items_dataset.csv", "price", "error"),
    ("DQ_NON_NEG_002", "olist_order_items_dataset.csv", "freight_value", "error"),
    ("DQ_NON_NEG_003", "olist_order_payments_dataset.csv", "payment_value", "error"),
    ("DQ_NON_NEG_004", "olist_order_reviews_dataset.csv", "review_score", "error"),
    ("DQ_NON_NEG_005", "olist_products_dataset.csv", "product_weight_g", "warning"),
    ("DQ_NON_NEG_006", "olist_products_dataset.csv", "product_length_cm", "warning"),
    ("DQ_NON_NEG_007", "olist_products_dataset.csv", "product_height_cm", "warning"),
    ("DQ_NON_NEG_008", "olist_products_dataset.csv", "product_width_cm", "warning"),
]
TIMESTAMP_RULES: list[tuple[str, str, str, str]] = [
    ("DQ_TS_001", "olist_orders_dataset.csv", "order_purchase_timestamp", "error"),
    ("DQ_TS_002", "olist_orders_dataset.csv", "order_approved_at", "warning"),
    ("DQ_TS_003", "olist_orders_dataset.csv", "order_delivered_carrier_date", "warning"),
    ("DQ_TS_004", "olist_orders_dataset.csv", "order_delivered_customer_date", "warning"),
    ("DQ_TS_005", "olist_orders_dataset.csv", "order_estimated_delivery_date", "error"),
    ("DQ_TS_006", "olist_order_items_dataset.csv", "shipping_limit_date", "error"),
    ("DQ_TS_007", "olist_order_reviews_dataset.csv", "review_creation_date", "error"),
    ("DQ_TS_008", "olist_order_reviews_dataset.csv", "review_answer_timestamp", "error"),
]
ORDER_STATUS_ALLOWED_VALUES = {
    "approved",
    "canceled",
    "created",
    "delivered",
    "invoiced",
    "processing",
    "shipped",
    "unavailable",
}

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def calculate_failure_percentage (failured_count: int, total_count: int) -> float:
    if total_count == 0:
        return 0.0
    return round((failured_count / total_count) * 100,2)

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
    status = "PASS" if failed_count == 0 else "FAIL"

    return RawQualityCheckResult(
        rule_id=rule_id,
        source_file=source_file,
        column_name=column_name,
        rule_type=rule_type,
        severity=severity,
        status=status,
        failed_count=int(failed_count),
        total_count=int(total_count),
        failure_percentage=calculate_failure_percentage(failed_count, total_count),
        message=message,
        checked_at=utc_now(),
    )

def check_expected_files_exist(raw_data_dir: Path) -> list [RawQualityCheckResult]:
    result :list[RawQualityCheckResult] = []
    for file_name in EXPECTED_OLIST_FILES:
        file_path = raw_data_dir / file_name
        file_exist = file_path.exists()

        result.append(
            build_result(
               rule_id = f"DQ_FILE_EXISTS_{file_name}" ,
               source_file = file_name,
               column_name=None,
               rule_type= "file_exists",
               severity='error',
               failed_count = 0 if file_exist else 1,
               total_count=1,
               message= 'Expected file exists' if file_exist else f"Expected file is missing: {file_name}"
            )
        )
    return result

def check_required_columns(df: pd.DataFrame,source_file: str,required_columns: list[str] ) -> list[RawQualityCheckResult]:
    results: list[RawQualityCheckResult] = []
    actual_columns = set(df.columns)

    for column_name in required_columns:
        column_exists = column_name in actual_columns

        results.append(
            build_result(
                rule_id=f"DQ_REQUIRED_COLUMN_{source_file}_{column_name}",
                source_file=source_file,
                column_name=column_name,
                rule_type="required_column_exists",
                severity="error",
                failed_count=0 if column_exists else 1,
                total_count=1,
                message=(
                    "Required column exists"
                    if column_exists
                    else f"Required column is missing: {column_name}"
                ),
            )
        )

    return results
def check_not_null(df: pd.DataFrame,source_file: str,column_name: str,rule_id: str,severity: str) -> RawQualityCheckResult:
    
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

    failed_count = int(df[column_name].isna().sum())
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
            "Column has no null values"
            if failed_count == 0
            else f"Column contains {failed_count} null values"
        ),
    )


def check_non_negative(df: pd.DataFrame,source_file: str,column_name: str,rule_id: str, severity: str) -> RawQualityCheckResult:
    if column_name not in df.columns:
        return build_result(
            rule_id=rule_id,
            source_file=source_file,
            column_name=column_name,
            rule_type="non_negative",
            severity=severity,
            failed_count=1,
            total_count=1,
            message=f"Column not found for non-negative check: {column_name}",
        )

    numeric_series = pd.to_numeric(df[column_name], errors="coerce")

    invalid_numeric_mask = df[column_name].notna() & numeric_series.isna()
    negative_mask = numeric_series < 0

    failed_count = int((invalid_numeric_mask | negative_mask).sum())
    total_count = len(df)

    return build_result(
        rule_id=rule_id,
        source_file=source_file,
        column_name=column_name,
        rule_type="non_negative",
        severity=severity,
        failed_count=failed_count,
        total_count=total_count,
        message=(
            "Column values are numeric and non-negative"
            if failed_count == 0
            else f"Column contains {failed_count} negative or non-numeric values"
        ),
    )


def check_parseable_timestamp(df: pd.DataFrame,source_file: str,column_name: str,rule_id: str,severity: str,) -> RawQualityCheckResult:
    if column_name not in df.columns:
        return build_result(
            rule_id=rule_id,
            source_file=source_file,
            column_name=column_name,
            rule_type="parseable_timestamp",
            severity=severity,
            failed_count=1,
            total_count=1,
            message=f"Column not found for timestamp check: {column_name}",
        )

    non_null_values = df[column_name].dropna()
    parsed_values = pd.to_datetime(non_null_values, errors="coerce")

    failed_count = int(parsed_values.isna().sum())
    total_count = len(non_null_values)

    return build_result(
        rule_id=rule_id,
        source_file=source_file,
        column_name=column_name,
        rule_type="parseable_timestamp",
        severity=severity,
        failed_count=failed_count,
        total_count=total_count,
        message=(
            "Non-null values are parseable as timestamps"
            if failed_count == 0
            else f"Column contains {failed_count} non-parseable timestamp values"
        ),
    )


def check_accepted_values(df: pd.DataFrame,source_file: str,column_name: str,allowed_values: set[str],rule_id: str,severity: str,) -> RawQualityCheckResult:
    if column_name not in df.columns:
        return build_result(
            rule_id=rule_id,
            source_file=source_file,
            column_name=column_name,
            rule_type="accepted_values",
            severity=severity,
            failed_count=1,
            total_count=1,
            message=f"Column not found for accepted-values check: {column_name}",
        )

    non_null_values = df[column_name].dropna().astype(str)
    invalid_mask = ~non_null_values.isin(allowed_values)

    failed_count = int(invalid_mask.sum())
    total_count = len(non_null_values)

    return build_result(
        rule_id=rule_id,
        source_file=source_file,
        column_name=column_name,
        rule_type="accepted_values",
        severity=severity,
        failed_count=failed_count,
        total_count=total_count,
        message=(
            "Column values are within the accepted set"
            if failed_count == 0
            else f"Column contains {failed_count} values outside the accepted set"
        ),
    )


def build_raw_quality_checks(raw_data_dir: Path,output_dir: Path,run_date: str,) -> Path:
    validate_row_data_dir(raw_data_dir)

    logger.info(
        "Raw data quality job started",
        extra={
            "raw_data_dir": str(raw_data_dir),
            "output_dir": str(output_dir),
            "run_date": run_date,
        },
    )

    quality_results: list[RawQualityCheckResult] = []

    quality_results.extend(check_expected_files_exist(raw_data_dir))

    for source_file, required_columns in EXPECTED_OLIST_FILES.items():
        file_path = raw_data_dir / source_file

        if not file_path.exists():
            logger.warning(
                "Skipping file-level checks because source file is missing",
                extra={"source_file": source_file},
            )
            continue

        logger.info(
            "Running raw data quality checks for file",
            extra={"source_file": source_file, "file_path": str(file_path)},
        )

        df = pd.read_csv(file_path)

        quality_results.extend(
            check_required_columns(
                df=df,
                source_file=source_file,
                required_columns=required_columns,
            )
        )

        for rule_id, rule_file, column_name, severity in NOT_NULL_RULES:
            if rule_file == source_file:
                quality_results.append(
                    check_not_null(
                        df=df,
                        source_file=source_file,
                        column_name=column_name,
                        rule_id=rule_id,
                        severity=severity,
                    )
                )

        for rule_id, rule_file, column_name, severity in NON_NEGATIVE_RULES:
            if rule_file == source_file:
                quality_results.append(
                    check_non_negative(
                        df=df,
                        source_file=source_file,
                        column_name=column_name,
                        rule_id=rule_id,
                        severity=severity,
                    )
                )

        for rule_id, rule_file, column_name, severity in TIMESTAMP_RULES:
            if rule_file == source_file:
                quality_results.append(
                    check_parseable_timestamp(
                        df=df,
                        source_file=source_file,
                        column_name=column_name,
                        rule_id=rule_id,
                        severity=severity,
                    )
                )

        if source_file == "olist_orders_dataset.csv":
            quality_results.append(
                check_accepted_values(
                    df=df,
                    source_file=source_file,
                    column_name="order_status",
                    allowed_values=ORDER_STATUS_ALLOWED_VALUES,
                    rule_id="DQ_ACCEPTED_VALUES_001",
                    severity="warning",
                )
            )

    run_output_dir = output_dir / f"run_date={run_date}"
    run_output_dir.mkdir(parents=True, exist_ok=True)

    output_file = run_output_dir / "raw_quality_checks.csv"

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
        "Raw data quality report written",
        extra={
            "output_file": str(output_file),
            "total_checks": len(quality_df),
            "failed_checks": failed_checks,
        },
    )

    return output_file


