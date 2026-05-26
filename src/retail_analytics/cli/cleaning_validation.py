import argparse
import logging
from datetime import date
from pathlib import Path
from retail_analytics.config import CLEANING_VALIDATION_REPORT_DIR,OLIST_DATA_DIR,OLIST_CLEAN_DATA_DIR
from retail_analytics.utils.logging import setup_logging
from retail_analytics.validation.cleaning_validation import validate_cleaned_outputs
from retail_analytics.validation.run_date import validate_run_date

logger = logging.getLogger(__name__)

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate cleaned Olist outputs before PostgreSQL loading."
    )

    parser.add_argument(
        "--raw-data-dir",
        type=Path,
        default=OLIST_DATA_DIR,
        help="Directory containing raw Olist CSV files.",
    )

    parser.add_argument(
        "--cleaned-data-dir",
        type=Path,
        default=OLIST_CLEAN_DATA_DIR,
        help="Base directory containing cleaned Olist outputs.",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=CLEANING_VALIDATION_REPORT_DIR,
        help="Directory where cleaning validation reports will be written.",
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

    logger.info("Cleaning validation CLI started",
        extra={
            "raw_data_dir": str(args.raw_data_dir),
            "cleaned_data_dir": str(args.cleaned_data_dir),
            "output_dir": str(args.output_dir),
            "run_date": args.run_date,
        },)
    output_file = validate_cleaned_outputs(
        raw_data_dir=args.raw_data_dir,
        cleaned_data_dir=args.cleaned_data_dir,
        output_dir=args.output_dir,
        run_date=args.run_date,
    )

    logger.info(
        "Cleaning validation CLI completed successfully",
        extra={"output_file": str(output_file)},
    )

if __name__ == "__main__":
    main()