import argparse
import logging
from datetime import date
from pathlib import Path

from retail_analytics.cleaning.olist_cleaner import build_olist_cleaned_files
from retail_analytics.config import CLEANING_REPORT_DIR,OLIST_CLEAN_DATA_DIR, OLIST_DATA_DIR

from retail_analytics.utils.logging import setup_logging
from retail_analytics.validation.run_date import validate_run_date

logger = logging.getLogger(__name__)

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Clean raw Olist CSV files and write cleaned local outputs."
    )

    parser.add_argument(
        "--raw-data-dir",
        type=Path,
        default=OLIST_DATA_DIR,
        help="Directory containing raw Olist CSV files.",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OLIST_CLEAN_DATA_DIR,
        help="Directory where cleaned Olist files will be written.",
    )

    parser.add_argument(
        "--report-dir",
        type=Path,
        default=CLEANING_REPORT_DIR,
        help="Directory where cleaning summary reports will be written.",
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
        "Olist cleaning CLI started",
        extra={
            "raw_data_dir": str(args.raw_data_dir),
            "output_dir": str(args.output_dir),
            "report_dir": str(args.report_dir),
            "run_date": args.run_date,
        },
    )

    summary_file = build_olist_cleaned_files(
        raw_data_dir=args.raw_data_dir,
        output_dir=args.output_dir,
        report_dir=args.report_dir,
        run_date=args.run_date,
    )

    logger.info(
        "Olist cleaning CLI completed successfully",
        extra={"summary_file": str(summary_file)},
    )


if __name__ == "__main__":
    main()