import pandas as pd  # type: ignore[import]
from datetime import datetime, timezone
import logging
import argparse
from dataclasses import  asdict

from pathlib import Path

from retail_analytics.config import DEFAULT_CHUNK_SIZE
from retail_analytics.utils import setup_logging

from retail_analytics.models.raw_inventory import CSVFileInventory
from retail_analytics.validation.raw_files import validate_csv_file_exist, validate_row_data_dir

logger = logging.getLogger(__name__)

def discover_csv_file(raw_data_path: Path) -> list[Path]:
    
    validate_row_data_dir(raw_data_path)
    csv_files = sorted(raw_data_path.glob("*.csv"))
    
    validate_csv_file_exist(csv_files,raw_data_path)

    logger.info("cvs files discovered.",
         extra={
                "raw_data_dir": str(raw_data_path),
                "csv_file_count": len(csv_files), 
                })
    return csv_files


def count_row (csv_path: Path,chunk_size: int = DEFAULT_CHUNK_SIZE) -> int:
    total_rows = 0
    for chunk in pd.read_csv(csv_path, chunksize= chunk_size):
         total_rows += len(chunk)
    return total_rows

def inspect_csv_file (csv_path: Path, chunk_size: int) -> CSVFileInventory:
    sample_df = pd.read_csv(csv_path, nrows = 1000)

    inventory = CSVFileInventory(
        file_name = csv_path.name,
        file_path = str(csv_path),
        row_count = count_row(csv_path,chunk_size),
        column_count = len(sample_df.columns),
        columns =  ", ".join(sample_df.columns),
        file_size_mb=round(csv_path.stat().st_size / (1024 * 1024), 2),
        inspected_at = datetime.now(timezone.utc).isoformat()
    )
    logger.info(
         "CSV file inspected",
         extra={
             "file_name": inventory.file_name,
             "file_path": inventory.file_path,
             "row_count": inventory.row_count,
             "column_count": inventory.column_count,
             "columns": inventory.columns,
             "file_size_mb": inventory.file_size_mb,
             "inspected_at": inventory.inspected_at

         }
     )
    return inventory

def build_raw_inventory(raw_data_dir: Path, output_dir: Path,run_date: str, chunk_size: int ) -> Path:
    csv_files = discover_csv_file(raw_data_dir)

    records= [
        asdict (inspect_csv_file(csv_file,chunk_size)) for csv_file in csv_files
    ]

    

    run_output_dir = output_dir / f"run_date={run_date}"
    run_output_dir.mkdir(parents=True, exist_ok=True)
    output_file = run_output_dir / "raw_file_inventory.csv"
    pd.DataFrame(records).to_csv(output_file,index=False)

    logger.info(
        "Raw inventory report written.",
        extra={
            "output_file": output_file,
            "file_count": len(records)
        }
    )
    return output_file




