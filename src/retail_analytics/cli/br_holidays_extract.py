from __future__ import annotations

import argparse
import logging
from datetime import date
from pathlib import Path

from retail_analytics.config import BR_HOLIDAYS_RAW_DATA_DIR
from retail_analytics.ingestion.extract_br_holidays import extract_br_holidays
from retail_analytics.utils.logging import setup_logging
from retail_analytics.validation.run_date import validate_run_date

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract Brazil public holidays from the Nager.Date API."
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=BR_HOLIDAYS_RAW_DATA_DIR,
        help="Directory where raw Brazil holidays API responses will be written.",
    )

    parser.add_argument(
        "--run-date",
        type=str,
        default=date.today().isoformat(),
        help="Logical run date in YYYY-MM-DD format.",
    )

    parser.add_argument(
        "--years",
        nargs="+",
        type=int,
        default=[2016, 2017, 2018],
        help="Holiday years to extract.",
    )

    parser.add_argument(
        "--country-code",
        type=str,
        default="BR",
        help="ISO country code. Default is BR.",
    )

    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=30,
        help="HTTP request timeout in seconds.",
    )

    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    setup_logging(args.log_level)
    validate_run_date(args.run_date)

    logger.info(
        "Brazil holidays extraction CLI started",
        extra={
            "output_dir": str(args.output_dir),
            "run_date": args.run_date,
            "years": args.years,
            "country_code": args.country_code,
        },
    )

    results = extract_br_holidays(
        output_dir=args.output_dir,
        run_date=args.run_date,
        years=args.years,
        country_code=args.country_code,
        timeout_seconds=args.timeout_seconds,
    )

    logger.info(
        "Brazil holidays extraction CLI completed successfully",
        extra={
            "file_count": len(results),
            "total_record_count": sum(result.record_count for result in results),
        },
    )


if __name__ == "__main__":
    main()