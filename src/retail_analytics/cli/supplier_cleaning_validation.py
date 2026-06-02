import argparse
import logging
from datetime import date
from pathlib import Path

from retail_analytics.cleaning.supplier_rules import (
    SUPPLIER_CLEAN_OUTPUT_FILE,
    SUPPLIER_SOURCE_FILE,
)
from retail_analytics.config import (
    SUPPLIER_CLEAN_DATA_DIR,
    SUPPLIER_CLEANING_VALIDATION_REPORT_DIR,
    SUPPLIER_RAW_DATA_DIR,
)
from retail_analytics.utils.logging import setup_logging
from retail_analytics.validation.supplier_cleaning_validation import (
    validate_supplier_cleaned_output,
)
from retail_analytics.validation.run_date import validate_run_date


logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate cleaned supplier output before PostgreSQL loading."
    )

    parser.add_argument(
        "--raw-data-dir",
        type=Path,
        default=SUPPLIER_RAW_DATA_DIR,
        help="Directory containing raw supplier files.",
    )

    parser.add_argument(
        "--cleaned-data-dir",
        type=Path,
        default=SUPPLIER_CLEAN_DATA_DIR,
        help="Base directory containing cleaned supplier outputs.",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=SUPPLIER_CLEANING_VALIDATION_REPORT_DIR,
        help="Directory where supplier cleaned validation reports will be written.",
    )

    parser.add_argument(
        "--source-file",
        type=str,
        default=SUPPLIER_SOURCE_FILE,
        help="Raw supplier source file name.",
    )

    parser.add_argument(
        "--cleaned-file",
        type=str,
        default=SUPPLIER_CLEAN_OUTPUT_FILE,
        help="Cleaned supplier output file name.",
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
        "Supplier cleaning validation CLI started",
        extra={
            "raw_data_dir": str(args.raw_data_dir),
            "cleaned_data_dir": str(args.cleaned_data_dir),
            "output_dir": str(args.output_dir),
            "source_file": args.source_file,
            "cleaned_file": args.cleaned_file,
            "run_date": args.run_date,
        },
    )

    output_file = validate_supplier_cleaned_output(
        raw_data_dir=args.raw_data_dir,
        cleaned_data_dir=args.cleaned_data_dir,
        output_dir=args.output_dir,
        run_date=args.run_date,
        source_file=args.source_file,
        cleaned_file=args.cleaned_file,
    )

    logger.info(
        "Supplier cleaning validation CLI completed successfully",
        extra={"output_file": str(output_file)},
    )


if __name__ == "__main__":
    main()