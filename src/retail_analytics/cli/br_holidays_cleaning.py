from __future__ import annotations

import argparse
import logging
from datetime import date
from pathlib import Path

from retail_analytics.cleaning.br_holidays_cleaner import build_br_holidays_cleaned_file

from retail_analytics.config import BR_HOLIDAYS_CLEAN_DATA_DIR,BR_HOLIDAYS_CLEANING_REPORT_DIR,BR_HOLIDAYS_RAW_DATA_DIR
from retail_analytics.utils import setup_logging
from retail_analytics.validation.run_date import validate_run_date

logger = logging.getLogger(__name__)
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Normalize raw Brazil public holiday API JSON files into a cleaned CSV."
        )
    )

    parser.add_argument(
        "--raw-data-dir",
        type=Path,
        default=BR_HOLIDAYS_RAW_DATA_DIR,
        help="Directory containing raw Brazil holidays API JSON files.",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=BR_HOLIDAYS_CLEAN_DATA_DIR,
        help="Directory where cleaned Brazil holidays output will be written.",
    )

    parser.add_argument(
        "--report-dir",
        type=Path,
        default=BR_HOLIDAYS_CLEANING_REPORT_DIR,
        help="Directory where Brazil holidays cleaning reports will be written.",
    )

    parser.add_argument(
        "--run-date",
        type=str,
        default=date.today().isoformat(),
        help="Logical run date in YYYY-MM-DD format.",
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
        "Brazil holidays cleaning CLI started",
        extra={
            "raw_data_dir": str(args.raw_data_dir),
            "output_dir": str(args.output_dir),
            "report_dir": str(args.report_dir),
            "run_date": args.run_date,
        },
    )

    result = build_br_holidays_cleaned_file(
        raw_data_dir=args.raw_data_dir,
        output_dir=args.output_dir,
        report_dir=args.report_dir,
        run_date=args.run_date,
    )

    logger.info(
        "Brazil holidays cleaning CLI completed successfully",
        extra={
            "output_file": result.output_file,
            "report_file": result.report_file,
            "output_row_count": result.output_row_count,
        },
    )


if __name__ == "__main__":
    main()