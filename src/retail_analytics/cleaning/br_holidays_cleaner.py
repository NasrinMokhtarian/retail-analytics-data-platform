from __future__ import annotations

import json
import logging
from pathlib import Path
from dataclasses import dataclass,asdict
from datetime import datetime, date, UTC
from typing import Any
import pandas as pd
from retail_analytics.ingestion.extract_br_holidays import BrHolidayExtractionResult

logger = logging.getLogger(__name__)

OUTPUT_COLUMNS = [
    "holiday_date",
    "holiday_name",
    "holiday_local_name",
    "country_code",
    "is_fixex",
    "is_global",
    "counties",
    "launch_year",
    "holiday_types",
    "source_system",
    "source_file_name",
    "extracted_at",
    "run_date"
]
@dataclass (frozen=True)
class HolidayCleaningResult:
    run_date: str
    input_dir: str
    output_file: str
    report_file: str
    input_file_count: int
    output_row_count: int
    cleaned_at: str

def read_json_file(path: Path) -> None:
    with path.open('r',encoding='utf-8') as file:
        return json.load(file)
def write_json_file(path: Path, data: Any) -> None:
     
     path.parent.mkdir(parents=True, exist_ok=True)
     with path.open('w', encoding='utf-8') as file:
         json.dump(data,file,ensure_ascii=False,indent=2)

def load_extraction_metadata(input_dir:Path) -> dict[str,str]:
    metadata_path = input_dir / 'extraction_metadata.json'

    if not metadata_path.exists():
        logger.warning(
            "Br holidays extraction metadata not found.",
            extra={"metadata_path": str(metadata_path),"metadata_type": type(metadata_path).__name__,}
        )
        return {}
    metadata = read_json_file(metadata_path)
    if not isinstance(metadata, list):
        logging.warning(
            "Unexpected BR holidays metadata format",
            extra={
                "metadata_path": str(metadata_path),
                "metadata_type": type(metadata).__name__,
            }
        )
        return{}
    metadata_by_file: dict[str,str]={}

    for item in metadata:
        if not isinstance (item, dict):
            continue
        output_file = item.get("output_file")
        extracted_at = item.get("extracted_at")

        if output_file and extracted_at:
            metadata_by_file[Path(output_file).name]= extracted_at
    return metadata_by_file

def serialize_optional_value(value: Any) -> str | None:
    if value is None:
        return None

    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)

    return str(value)

def normalize_holiday_record(
    record: dict[str, Any],
    source_file_name: str,
    extracted_at: str | None,
    run_date: str,
) -> dict[str, Any]:
    return {
        "holiday_date": record.get("date"),
        "holiday_name": record.get("name"),
        "holiday_local_name": record.get("localName"),
        "country_code": record.get("countryCode"),
        "is_fixed": record.get("fixed"),
        "is_global": record.get("global"),
        "counties": serialize_optional_value(record.get("counties")),
        "launch_year": record.get("launchYear"),
        "holiday_types": serialize_optional_value(record.get("types")),
        "source_system": "nager_date",
        "source_file_name": source_file_name,
        "extracted_at": extracted_at,
        "run_date": run_date,
    }

def normalize_holiday_files(input_dir: Path, run_date: str) -> pd.DataFrame:
    json_files = sorted(input_dir.glob("br_public_holidays_*.json"))

    if not json_files:
        raise FileNotFoundError(
            f"No Brazil holiday JSON files found in input directory: {input_dir}"
        )

    metadata_by_file = load_extraction_metadata(input_dir)
    normalized_records: list[dict[str, Any]] = []

    for json_file in json_files:
        logger.info(
            "Normalizing Brazil holidays file",
            extra={"source_file": str(json_file)},
        )

        raw_data = read_json_file(json_file)

        if not isinstance(raw_data, list):
            raise TypeError(
                f"Expected {json_file} to contain a JSON list, "
                f"got {type(raw_data).__name__}."
            )

        extracted_at = metadata_by_file.get(json_file.name)

        for record in raw_data:
            if not isinstance(record, dict):
                raise TypeError(
                    f"Expected holiday record in {json_file} to be a JSON object, "
                    f"got {type(record).__name__}."
                )

            normalized_records.append(
                normalize_holiday_record(
                    record=record,
                    source_file_name=json_file.name,
                    extracted_at=extracted_at,
                    run_date=run_date,
                )
            )

    df = pd.DataFrame(normalized_records)

    if df.empty:
        raise ValueError("Brazil holidays cleaned dataframe is empty.")

    for column in OUTPUT_COLUMNS:
        if column not in df.columns:
            df[column] = None

    df = df[OUTPUT_COLUMNS].copy()

    df["holiday_date"] = pd.to_datetime(df["holiday_date"], errors="coerce").dt.date
    df["run_date"] = pd.to_datetime(df["run_date"], errors="coerce").dt.date
    df["extracted_at"] = pd.to_datetime(df["extracted_at"], errors="coerce")

    df["country_code"] = df["country_code"].astype("string").str.upper().str.strip()
    df["holiday_name"] = df["holiday_name"].astype("string").str.strip()
    df["holiday_local_name"] = df["holiday_local_name"].astype("string").str.strip()

    df = df.sort_values(["holiday_date", "holiday_name"]).reset_index(drop=True)

    return df

def write_cleaned_output(df: pd.DataFrame, output_file: Path) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_file, index=False, encoding="utf-8")

def build_br_holidays_cleaned_file(
    raw_data_dir: Path,
    output_dir: Path,
    report_dir: Path,
    run_date: str,
) -> HolidayCleaningResult:
    input_dir = raw_data_dir / f"run_date={run_date}"
    output_run_dir = output_dir / f"run_date={run_date}"
    report_run_dir = report_dir / f"run_date={run_date}"

    output_file = output_run_dir / "br_holidays_clean.csv"
    report_file = report_run_dir / "br_holidays_cleaning_summary.json"

    if not input_dir.exists():
        raise FileNotFoundError(
            f"Brazil holidays raw input directory does not exist: {input_dir}"
        )

    logger.info(
        "Brazil holidays cleaning started",
        extra={
            "input_dir": str(input_dir),
            "output_file": str(output_file),
            "report_file": str(report_file),
            "run_date": run_date,
        },
    )

    df = normalize_holiday_files(input_dir=input_dir, run_date=run_date)
    write_cleaned_output(df=df, output_file=output_file)

    result = HolidayCleaningResult(
        run_date=run_date,
        input_dir=str(input_dir),
        output_file=str(output_file),
        report_file=str(report_file),
        input_file_count=len(list(input_dir.glob("br_public_holidays_*.json"))),
        output_row_count=len(df),
        cleaned_at=datetime.now(UTC).isoformat(),
    )

    write_json_file(report_file, asdict(result))

    logger.info(
        "Brazil holidays cleaning completed successfully",
        extra={
            "output_file": str(output_file),
            "report_file": str(report_file),
            "output_row_count": len(df),
        },
    )

    return result




