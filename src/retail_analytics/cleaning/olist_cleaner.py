import logging
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd # type: ignore [import] 

from retail_analytics.cleaning.olist_rules import STRING_COLUMNS,NUMERIC_COLUMNS,TIMESTAMP_COLUMNS,OLIST_OUTPUT_FILE_NAMES

from retail_analytics.models.cleaning import CleanedFileResult
from retail_analytics.validation.raw_files import validate_row_data_dir

logger = logging.getLogger(__name__)

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def get_read_dtypes(source_file: str) -> dict[str,str]:
    """
    Read selected columns as strings from the beginning.

    This is especially important for identifiers and zip-code-like fields.
    """

    return {column_name: "string" for column_name in STRING_COLUMNS.get(source_file,[])}

def normalize_text_columns(df: pd.DataFrame, source_file:str) -> pd.DataFrame:
    """
    Trim text columns and convert empty strings to null values.
    """
    cleaned_df = df.copy()
    string_columns = STRING_COLUMNS.get(source_file,[])

    for column_name in string_columns:
        if column_name in cleaned_df.columns:
            cleaned_df[column_name] = ( cleaned_df[column_name].astype('string').str.strip().replace('',pd.NA))
    
    object_columns = cleaned_df.select_dtypes(include=['object']).columns

    for column_name in object_columns:
        cleaned_df[column_name] = cleaned_df[column_name].astype('string').str.strip().replace('',pd.NA)

    return cleaned_df

def parse_timestamp_columns(df: pd.DataFrame, source_file: str) -> tuple[pd.DataFrame,int,int]:
    """
    Parse configured timestamp columns.

    Returns:
        cleaned dataframe,
        number of timestamp columns processed,
        number of invalid non-null timestamp values
    """
    cleaned_df = df.copy()
    invalid_timestamp_count = 0
    processed_timestamp_columns = 0
    for column_name in TIMESTAMP_COLUMNS.get(source_file, []):
        if column_name not in cleaned_df.columns:
            continue
        original_series =  cleaned_df[column_name]
        not_null_mask = original_series.notna()
        parsed_series = pd.to_datetime(original_series,errors = 'coerce')
        
        invalid_mask = not_null_mask & parsed_series.isna()
        invalid_timestamp_count += int(invalid_mask.sum())
        
        cleaned_df[column_name] = parsed_series
        processed_timestamp_columns +=1

    return cleaned_df,invalid_timestamp_count,processed_timestamp_columns

def convert_numeric_columns(df: pd.DataFrame, source_file: str) -> tuple[pd.DataFrame,int,int]:
    """
    Convert configured numeric columns.

    Returns:
        cleaned dataframe,
        number of numeric columns processed,
        number of invalid non-null numeric values
    """
    cleaned_df = df.copy()
    invalid_numeric_count =0
    processed_numeric_columns = 0
    for column_name in NUMERIC_COLUMNS.get(source_file,[]):
        if column_name not in cleaned_df.columns:
            continue
        original_series = cleaned_df[column_name]
        non_null_mask = original_series.notna()
        numeric_series = pd.to_numeric(original_series, errors='coerce')
        invalid_mask = non_null_mask & numeric_series.isna()
        invalid_numeric_count += int(invalid_mask.sum())

        cleaned_df[column_name] = numeric_series
        processed_numeric_columns +=1
    
    return cleaned_df, invalid_numeric_count, processed_numeric_columns

def add_metadata_columns(df: pd.DataFrame, source_file: str, run_date: str,ingested_at: str) -> pd.DataFrame:
    """
    Add metadate to cleaned dataframe
    """
    cleaned_df = df.copy()
    cleaned_df['source_file_name'] = source_file
    cleaned_df['ingested_at'] = ingested_at
    cleaned_df['run_date'] = run_date
    
    return cleaned_df
def clean_olist_file(csv_path: Path,output_dir: Path, run_date: str) -> CleanedFileResult:
    source_file = csv_path.name
    output_file = output_dir /OLIST_OUTPUT_FILE_NAMES[source_file]
    cleaned_at = utc_now()
    
    logger.info(
        "Cleaning Olist source file started.",
        extra = {"source_file": source_file, "output_file": str(output_file), "input_file": str(csv_path) })
    df =pd.read_csv(csv_path, dtype = get_read_dtypes(source_file))

    df = normalize_text_columns(df,source_file)
    df, invalid_timestamp_count, processed_timestamp_columns = parse_timestamp_columns(df,source_file)

    df,invalid_numeric_count, processed_numeric_columns = convert_numeric_columns(df, source_file)
    df = add_metadata_columns(df=df, source_file=source_file, run_date=run_date, ingested_at=cleaned_at)
    
    output_dir.mkdir(parents =True, exist_ok = True)
    df.to_csv(output_file, index=False)

    result = CleanedFileResult(
        source_file=source_file,
        output_file=str(output_file),
        row_count=len(df),
        column_count=len(df.columns),
        timestamp_columns_processed=processed_timestamp_columns,
        numeric_column_processed=processed_numeric_columns,
        invalid_timestamp_count=invalid_timestamp_count,
        invalid_numeric_count=invalid_numeric_count,
        cleaned_at=cleaned_at
    )
    logger.info(
        "Cleaning Olist source file completed",
        extra=asdict(result),
    )
    return result

def build_olist_cleaned_files(raw_data_dir: Path, output_dir: Path, report_dir: Path,run_date: str) ->  Path:
    validate_row_data_dir(raw_data_dir)
    run_output_dir = output_dir / f"run_date={run_date}"
    run_report_dir = report_dir / f"run_date={run_date}"

    cleaning_result: list[CleanedFileResult] = []
    logger.info(
        "Olist cleaning job started",
        extra={
            "raw_data_dir": str(raw_data_dir),
            "output_dir": str(run_output_dir),
            "report_dir": str(run_report_dir),
            "run_date": run_date,
        },
    )
    for source_file in OLIST_OUTPUT_FILE_NAMES:
        csv_path = raw_data_dir / source_file
        if not csv_path.exists():
            logger.error(f" Expected source fle missing during vleaning job",
                         extra={"source_file": source_file, "file_path": str(csv_path)})
            raise FileNotFoundError(f"Expected source file is missing: {csv_path}")
        result = clean_olist_file(csv_path,run_output_dir,run_date)
        cleaning_result.append(result)
    
    run_report_dir.mkdir(parents=True, exist_ok=True)
    summary_file = run_report_dir / "cleaning_summary.csv"
    summary_df =  pd.DataFrame(asdict(result) for result in cleaning_result)
    summary_df.to_csv(summary_file, index=False)
    logger.info(
        "Olist cleaning job completed",
        extra={
                "cleaned_file_count": len(cleaning_result),
                "summary_file": str(summary_file),
                "total_rows": int(summary_df["row_count"].sum()),
                "invalid_timestamp_count": int(summary_df["invalid_timestamp_count"].sum()),
                "invalid_numeric_count": int(summary_df["invalid_numeric_count"].sum()),
        },
    )
    return summary_file






