import logging
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd # type: ignore [import] 

from retail_analytics.cleaning.supplier_rules import ALLOWED_CURRENCIES,ALLOWED_STOCK_STATUSES,TEXT_COLUMNS,BUSINESS_KEY_COLUMNS,SUPPLIER_SOURCE_FILE,SUPPLIER_CLEAN_OUTPUT_FILE
from retail_analytics.models.supplier_cleaning import SupplierCleaningResult
from retail_analytics.validation.raw_files import validate_row_data_dir

logger = logging.getLogger(__name__)

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def normalize_text_value(series: pd.Series) -> pd.Series:
    """
    Trim text columns and convert empty strings to null values.
    """
    return series.astype(str).str.strip().replace('', pd.NA)

def normalize_price(series: pd.Series) -> pd.Series:
    return (
        series.astype("string")
        .str.strip()
        .str.replace(",", ".", regex=False)
        .replace("", pd.NA)
    )

def normalize_currency(series: pd.Series) -> pd.Series:
    """
    Normalize currency values to strip,uppercase and empty strings to null
    """
    return series.astype(str).str.strip().str.upper().replace('', pd.NA)  

def normalize_stock_status(series: pd.Series) -> pd.Series:
    """
    Normalize stock status values to strip,uppercase and empty strings to null
    """
    return series.astype(str).str.strip().str.upper().replace(' ', '_',regex=True).replace('', pd.NA)

def parse_datetime_flexible(series: pd.Series) -> pd.Series:
    """
    Attempt to parse mixed date/datetime formats.
    The supplier file intentionally containes mixed formats, so this function uses pandas mixed parsing where available.
    """
    normalized=normalize_text_value(series)

    try:
        return pd.to_datetime(normalized, errors = 'coerce',format = 'mixed')
    except TypeError:
        return pd.to_datetime(normalized, errors = 'coerce')
    
def clean_supplier_dataframe(df: pd.DataFrame,source_file: str, run_date: str, cleaned_at: str) -> pd.DataFrame:
    cleaned_df=df.copy()
    for column_name in TEXT_COLUMNS:
        if column_name in cleaned_df.columns:
            cleaned_df[column_name] = normalize_text_value(cleaned_df[column_name])
    cleaned_df['currency_clean'] = normalize_currency(cleaned_df['currency'])
    cleaned_df['stock_status_clean'] = normalize_stock_status(cleaned_df['stock_status'])
    normalized_price = normalize_price(cleaned_df['updated_price'])
    cleaned_df['updated_price_clean'] = pd.to_numeric(normalized_price, errors='coerce')
    cleaned_df["valid_from_clean"] = parse_datetime_flexible(cleaned_df["valid_from"]).dt.date

    cleaned_df["last_updated_at_clean"] = parse_datetime_flexible(cleaned_df["last_updated_at"])

    cleaned_df["has_missing_product_id"] = cleaned_df["product_id"].isna()
    cleaned_df["has_missing_currency"] = cleaned_df["currency_clean"].isna()

    cleaned_df["has_invalid_price"] = (cleaned_df["updated_price"].notna()& cleaned_df["updated_price_clean"].isna())

    cleaned_df["has_negative_price"] = cleaned_df["updated_price_clean"] < 0

    cleaned_df["has_unknown_stock_status"] = (cleaned_df["stock_status_clean"].notna()& ~cleaned_df["stock_status_clean"].isin(ALLOWED_STOCK_STATUSES))

    cleaned_df["has_missing_valid_from"] = cleaned_df["valid_from"].isna()

    cleaned_df["has_invalid_valid_from"] = (cleaned_df["valid_from"].notna()& pd.isna(cleaned_df["valid_from_clean"]))

    cleaned_df["has_invalid_last_updated_at"] = (cleaned_df["last_updated_at"].notna()& cleaned_df["last_updated_at_clean"].isna())

    business_key_df = cleaned_df[BUSINESS_KEY_COLUMNS].copy()

    for column_name in BUSINESS_KEY_COLUMNS:
        business_key_df[column_name] = normalize_text_value(business_key_df[column_name])

    cleaned_df["is_duplicate_business_key"] = business_key_df.duplicated(subset=BUSINESS_KEY_COLUMNS,keep=False,)

    cleaned_df["source_file_name"] = source_file
    cleaned_df["ingested_at"] = cleaned_at
    cleaned_df["run_date"] = run_date

    return cleaned_df

def build_supplier_cleaning_result(
    cleaned_df: pd.DataFrame,
    source_file: str,
    output_file: Path,
    cleaned_at: str,
) -> SupplierCleaningResult:
    return SupplierCleaningResult(
        source_file=source_file,
        output_file=str(output_file),
        row_count=len(cleaned_df),
        column_count=len(cleaned_df.columns),
        missing_product_id_count=int(cleaned_df["has_missing_product_id"].sum()),
        missing_currency_count=int(cleaned_df["has_missing_currency"].sum()),
        invalid_price_count=int(cleaned_df["has_invalid_price"].sum()),
        negative_price_count=int(cleaned_df["has_negative_price"].sum()),
        unknown_stock_status_count=int(cleaned_df["has_unknown_stock_status"].sum()),
        invalid_valid_from_count=int(cleaned_df["has_invalid_valid_from"].sum()),
        invalid_last_updated_at_count=int(cleaned_df["has_invalid_last_updated_at"].sum()),
        duplicate_business_key_count=int(cleaned_df["is_duplicate_business_key"].sum()),
        cleaned_at=cleaned_at,
    )


def clean_supplier_file(raw_data_dir: Path,output_dir: Path,report_dir: Path,run_date: str,source_file: str = SUPPLIER_SOURCE_FILE,) -> Path:
    validate_row_data_dir(raw_data_dir)

    source_file_path = raw_data_dir / source_file

    if not source_file_path.exists():
        raise FileNotFoundError(f"Supplier source file is missing: {source_file_path}")

    run_output_dir = output_dir / f"run_date={run_date}"
    run_report_dir = report_dir / f"run_date={run_date}"

    run_output_dir.mkdir(parents=True, exist_ok=True)
    run_report_dir.mkdir(parents=True, exist_ok=True)

    output_file = run_output_dir / SUPPLIER_CLEAN_OUTPUT_FILE
    summary_file = run_report_dir / "supplier_cleaning_summary.csv"

    cleaned_at = utc_now()

    logger.info(
        "Supplier cleaning job started",
        extra={
            "source_file": source_file,
            "source_file_path": str(source_file_path),
            "output_file": str(output_file),
            "summary_file": str(summary_file),
            "run_date": run_date,
        },
    )

    df = pd.read_csv(
        source_file_path,
        dtype={column_name: "string" for column_name in TEXT_COLUMNS},
    )

    cleaned_df = clean_supplier_dataframe(
        df=df,
        source_file=source_file,
        run_date=run_date,
        cleaned_at=cleaned_at,
    )

    cleaned_df.to_csv(output_file, index=False)

    result = build_supplier_cleaning_result(
        cleaned_df=cleaned_df,
        source_file=source_file,
        output_file=output_file,
        cleaned_at=cleaned_at,
    )

    summary_df = pd.DataFrame([asdict(result)])
    summary_df.to_csv(summary_file, index=False)

    logger.info(
        "Supplier cleaning job completed",
        extra=asdict(result),
    )

    return summary_file