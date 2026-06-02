import argparse
import logging
from datetime import date
from pathlib import Path

from retail_analytics.cleaning.supplier_cleaner import clean_supplier_file
from retail_analytics.cleaning.supplier_rules import SUPPLIER_SOURCE_FILE
from retail_analytics.config import (
    SUPPLIER_CLEAN_DATA_DIR,
    SUPPLIER_CLEANING_REPORT,
    SUPPLIER_RAW_DATA_DIR,
)
from retail_analytics.utils.logging import setup_logging
from retail_analytics.validation.run_date import validate_run_date


logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Clean handmade supplier product update source file."
    )

    parser.add_argument(
        "--raw-data-dir",
        type=Path,
        default=SUPPLIER_RAW_DATA_DIR,
        help="Directory containing raw supplier files.",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=SUPPLIER_CLEAN_DATA_DIR,
        help="Directory where cleaned supplier files will be written.",
    )

    parser.add_argument(
        "--report-dir",
        type=Path,
        default=SUPPLIER_CLEANING_REPORT,
        help="Directory where supplier cleaning reports will be written.",
    )

    parser.add_argument(
        "--source-file",
        type=str,
        default=SUPPLIER_SOURCE_FILE,
        help="Supplier source file name.",
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
        "Supplier cleaning CLI started",
        extra={
            "raw_data_dir": str(args.raw_data_dir),
            "output_dir": str(args.output_dir),
            "report_dir": str(args.report_dir),
            "source_file": args.source_file,
            "run_date": args.run_date,
        },
    )

    summary_file = clean_supplier_file(
        raw_data_dir=args.raw_data_dir,
        output_dir=args.output_dir,
        report_dir=args.report_dir,
        run_date=args.run_date,
        source_file=args.source_file,
    )

    logger.info(
        "Supplier cleaning CLI completed successfully",
        extra={"summary_file": str(summary_file)},
    )


if __name__ == "__main__":
    main()