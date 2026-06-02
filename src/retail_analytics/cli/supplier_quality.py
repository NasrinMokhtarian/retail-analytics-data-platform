import argparse
import logging
from datetime import date
from pathlib import Path

from retail_analytics.config import SUPPLIER_QUALITY_REPORT_DIR,SUPPLIER_RAW_DATA_DIR

from retail_analytics.quality.supplier_quality import DEFAULT_SUPPLIER_SOURCE_FILE,build_supplier_quality_checks

from retail_analytics.utils.logging import setup_logging
from retail_analytics.validation.run_date import validate_run_date


logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run supplier source quality checks."
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
        default=SUPPLIER_QUALITY_REPORT_DIR,
        help="Directory where supplier quality reports will be written.",
    )

    parser.add_argument(
        "--source-file",
        type=str,
        default=DEFAULT_SUPPLIER_SOURCE_FILE,
        help="Supplier source file name to quality check.",
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
        "Supplier quality CLI started",
        extra={
            "raw_data_dir": str(args.raw_data_dir),
            "output_dir": str(args.output_dir),
            "source_file": args.source_file,
            "run_date": args.run_date,
        },
    )

    output_file = build_supplier_quality_checks(
        raw_data_dir=args.raw_data_dir,
        output_dir=args.output_dir,
        run_date=args.run_date,
        source_file=args.source_file,
    )

    logger.info(
        "Supplier quality CLI completed successfully",
        extra={"output_file": str(output_file)},
    )


if __name__ == "__main__":
    main()
