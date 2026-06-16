from __future__ import annotations

import argparse
import logging
from datetime import date
from pathlib import Path

from retail_analytics.config import (
    BR_HOLIDAYS_CLEAN_DATA_DIR,
    BR_HOLIDAYS_CLEANING_VALIDATION_REPORT_DIR,
    BR_HOLIDAYS_RAW_DATA_DIR,
)
from retail_analytics.utils.logging import setup_logging
from retail_analytics.validation.br_holidays_cleaning_validation import (
    BR_HOLIDAYS_CLEAN_OUTPUT_FILE,
    validate_br_holidays_cleaned_output,
)
from retail_analytics.validation.run_date import validate_run_date

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate cleaned Brazil holidays output before PostgreSQL loading."
    )

    parser.add_argument(
        "--raw-data-dir",
        type=Path,
        default=BR_HOLIDAYS_RAW_DATA_DIR,
        help="Base directory containing raw Brazil holidays API responses.",
    )

    parser.add_argument(
        "--cleaned-data-dir",
        type=Path,
        default=BR_HOLIDAYS_CLEAN_DATA_DIR,
        help="Base directory containing cleaned Brazil holidays output.",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=BR_HOLIDAYS_CLEANING_VALIDATION_REPORT_DIR,
        help="Directory where Brazil holidays cleaned validation reports will be written.",
    )

    parser.add_argument(
        "--source-file",
        type=str,
        default="br_public_holidays_*.json",
        help="Raw Brazil holidays source file pattern.",
    )

    parser.add_argument(
        "--cleaned-file",
        type=str,
        default=BR_HOLIDAYS_CLEAN_OUTPUT_FILE,
        help="Cleaned Brazil holidays output file name.",
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
        "Brazil holidays cleaning validation CLI started",
        extra={
            "raw_data_dir": str(args.raw_data_dir),
            "cleaned_data_dir": str(args.cleaned_data_dir),
            "output_dir": str(args.output_dir),
            "source_file": args.source_file,
            "cleaned_file": args.cleaned_file,
            "run_date": args.run_date,
        },
    )

    output_file = validate_br_holidays_cleaned_output(
        raw_data_dir=args.raw_data_dir,
        cleaned_data_dir=args.cleaned_data_dir,
        output_dir=args.output_dir,
        run_date=args.run_date,
        source_file=args.source_file,
        cleaned_file=args.cleaned_file,
    )

    logger.info(
        "Brazil holidays cleaning validation CLI completed successfully",
        extra={"output_file": str(output_file)},
    )


if __name__ == "__main__":
    main()