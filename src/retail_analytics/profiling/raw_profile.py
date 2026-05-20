import json
import logging
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd # type: ignore[import]

from retail_analytics.config import DEAFULT_SAMPLE_VALUES_LIMIT
from retail_analytics.models.raw_profile import RawColumnProfile
from retail_analytics.validation.raw_files import validate_row_data_dir,validate_csv_file_exist

logger =logging.getLogger(__name__)

def discover_csv_files(raw_data_dir: Path) -> list[Path]:
    validate_row_data_dir(raw_data_dir)
    csv_files = sorted(raw_data_dir.glob('*.csv'))
    validate_csv_file_exist(csv_files,raw_data_dir)

    logger.info("cvs files discovered for profiling.",
         extra={
                "raw_data_dir": str(raw_data_dir),
                "csv_file_count": len(csv_files), 
                })
    return csv_files
        
def get_sample_values(series: pd.Series,sample_limit: int = DEAFULT_SAMPLE_VALUES_LIMIT )-> str:
    sample_values = (
        series.dropna()
        .astype(str)
        .drop_duplicates()
        .head(sample_limit)
        .tolist()
    )
    return json.dumps(sample_values,ensure_ascii = False)


def profile_column(file_name: str, column_name: str,series: pd.Series, row_count: int) -> RawColumnProfile:
    null_count = int(series.isna().sum())
    non_null_count = int(row_count - null_count)
    if row_count ==0:
        null_percentage = 0.0
    else:
        null_percentage = round((null_count/row_count)*100,2)

    return RawColumnProfile(
        file_name = file_name,
        column_name = column_name,
        column_dtype = str(series.dtype),
        row_count = row_count,
        null_count = null_count,
        null_percentage = null_percentage,
        non_null_count= non_null_count,
        distinct_count = int(series.nunique(dropna = True)),
        sample_values= get_sample_values(series),
        profiled_at = datetime.now(timezone.utc).isoformat()
    )

def profile_csv_file(csv_path: Path) -> list[RawColumnProfile]:
    logger.info(
        "Starting CSV column profiling",
        extra = {
            "file_name": csv_path.name,
            "file_path":str(csv_path)
        }
    )

    df = pd.read_csv(csv_path)
    row_count = len(df)
    column_profiles = [
                        profile_column(file_name = csv_path.name, column_name = column_name,series= df[column_name],row_count = row_count)
                        for column_name in df.columns
                        ]
    logger.info(
        "profiling CSV column completed",
        extra = {
            "file_name": csv_path.name,
            "file_path":str(csv_path),
            "column_count":len(df.columns)
        }
    )

    return column_profiles
            
def build_raw_profile(raw_data_dir:Path, output_dir:Path, run_date:str) -> Path:
    csv_files = discover_csv_files(raw_data_dir)
    profile_records: list[dict]=[]
    try:
        for csv_file in csv_files:
            column_profile = profile_csv_file(csv_file)
            for profile in column_profile:
                profile_records.append(asdict(profile))

    except Exception:
        logger.exception(
           "CSV column profiling failed",
                extra={
                    "file_name": csv_file.name,
                    "file_path": str(csv_file),
                } 
        )
        raise
    run_output_dir = output_dir / f"run_date = {run_date}"
    run_output_dir.mkdir(parents = True, exist_ok= True)

    output_file = run_output_dir / "raw_column_profile.csv"
    output_columns = [
        "file_name",
        "column_name",
        "column_dtype",
        "row_count",
        "null_count",
        "null_percentage",
        "non_null_count",
        "distinct_count",
        "sample_values",
        "profiled_at",
    ]  
    profile_df = pd.DataFrame(profile_records) 
    profile_df = profile_df[output_columns]
    profile_df.to_csv(output_file, index = False)
    logger.info(
        "Raw column profile report written",
        extra={
            "output_file": str(output_file),
            "profiled_column_count": len(profile_df),
            "profiled_file_count": len(csv_files),
        },
    )

    return output_file


        

