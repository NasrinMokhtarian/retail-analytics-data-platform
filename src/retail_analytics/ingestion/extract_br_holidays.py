from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from retail_analytics.config import NAGER_PUBLIC_HOLIDAYS_URL

import requests

logger = logging.getLogger(__name__)



@dataclass(frozen=True)
class BrHolidayExtractionResult:
    year: int
    country_code: str
    url: str
    output_file: str
    record_count: int
    status_code: int
    extracted_at: str


def write_json_file(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def fetch_public_holidays(
    year: int,
    country_code: str,
    timeout_seconds: int,
) -> tuple[list[dict[str, Any]], str, int]:
    country_code = country_code.upper()

    url = NAGER_PUBLIC_HOLIDAYS_URL.format(
        year=year,
        country_code=country_code,
    )

    logger.info(
        "Fetching Brazil public holidays from API",
        extra={
            "year": year,
            "country_code": country_code,
            "url": url,
        },
    )

    response = requests.get(url, timeout=timeout_seconds)

    if response.status_code != 200:
        raise RuntimeError(
            "Brazil holidays API request failed. "
            f"year={year}, country_code={country_code}, "
            f"status_code={response.status_code}, response={response.text[:500]}"
        )

    data = response.json()

    if not isinstance(data, list):
        raise TypeError(
            f"Expected API response to be a list, got {type(data).__name__}."
        )

    return data, url, response.status_code


def extract_br_holidays(
    output_dir: Path,
    run_date: str,
    years: list[int],
    country_code: str = "BR",
    timeout_seconds: int = 30,
) -> list[BrHolidayExtractionResult]:
    country_code = country_code.upper()
    output_run_dir = output_dir / f"run_date={run_date}"
    extracted_at = datetime.now(UTC).isoformat()

    logger.info(
        "Brazil holidays extraction started",
        extra={
            "output_dir": str(output_run_dir),
            "run_date": run_date,
            "years": years,
            "country_code": country_code,
        },
    )

    results: list[BrHolidayExtractionResult] = []

    for year in years:
        data, url, status_code = fetch_public_holidays(
            year=year,
            country_code=country_code,
            timeout_seconds=timeout_seconds,
        )

        output_file = (
            output_run_dir / f"{country_code.lower()}_public_holidays_{year}.json"
        )

        write_json_file(output_file, data)

        result = BrHolidayExtractionResult(
            year=year,
            country_code=country_code,
            url=url,
            output_file=str(output_file),
            record_count=len(data),
            status_code=status_code,
            extracted_at=extracted_at,
        )

        results.append(result)

        logger.info(
            "Saved Brazil holidays raw API response",
            extra={
                "year": year,
                "country_code": country_code,
                "record_count": len(data),
                "output_file": str(output_file),
            },
        )

    metadata_file = output_run_dir / "extraction_metadata.json"
    write_json_file(metadata_file, [asdict(result) for result in results])

    logger.info(
        "Brazil holidays extraction completed successfully",
        extra={
            "metadata_file": str(metadata_file),
            "file_count": len(results),
            "total_record_count": sum(result.record_count for result in results),
        },
    )

    return results