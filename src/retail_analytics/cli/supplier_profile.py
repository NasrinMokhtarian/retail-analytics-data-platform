import argparse
import logging
from datetime import date
from pathlib import Path
from retail_analytics.utils.logging import setup_logging
from retail_analytics.config import SUPPLIER_PROFILE_REPORT_DIR,DEFAULT_SAMPLE_VALUES_LIMIT,SUPPLIER_RAW_DATA_DIR
from retail_analytics.profiling.raw_profile import build_raw_profile
from retail_analytics.validation.run_date import validate_run_date

logger = logging.getLogger(__name__)

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build supplier column profile report."
    )

    parser.add_argument(
        "--raw-data-dir",
        type=Path,
        default=SUPPLIER_RAW_DATA_DIR,
        help="Directory containing raw supplier CSV files.",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=SUPPLIER_PROFILE_REPORT_DIR,
        help="Directory where the supplier profile report will be written.",
    )

    parser.add_argument(
        "--run-date",
        type=str,
        default= date.today().isoformat(),
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
        "Supplier column profiling CLI started",
        extra={
            "raw_data_dir":str(args.raw_data_dir),
            "output_dir":str(args.output_dir),
            "run_date":args.run_date,
        },
    )
    output_file = build_raw_profile(
        raw_data_dir=args.raw_data_dir,
        output_dir=args.output_dir,
        run_date=args.run_date,
        output_filename="supplier_column_profile.csv"
    )
    logger.info(
        "Supplier column profiling CLI completed successfully",
        extra={"output_file":str(output_file)},
    )

if __name__== "__main__":
    main()