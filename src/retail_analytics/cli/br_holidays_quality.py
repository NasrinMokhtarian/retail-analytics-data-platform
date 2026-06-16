from __future__ import annotations

import argparse
import logging
from datetime import date
from pathlib import Path

from retail_analytics.config import (
    BR_HOLIDAYS_CLEAN_DATA_DIR,
    BR_HOLIDAYS_QUALITY_REPORT_DIR,
)
from retail_analytics.quality.br_holidays_quality import (
    DEFAULT_BR_HOLIDAYS_CLEAN_FILE,
    build_br_holidays_quality_checks,
)
from retail_analytics.utils.logging import setup_logging
from retail_analytics.validation.run_date import validate_run_date

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run quality checks for cleaned Brazil holidays data."
    )

    parser.add_argument(
        "--clean-data-dir",
        type=Path,
        default=BR_HOLIDAYS_CLEAN_DATA_DIR,
        help="Directory containing cleaned Brazil holidays files.",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=BR_HOLIDAYS_QUALITY_REPORT_DIR,
        help="Directory where Brazil holidays quality reports will be written.",
    )

    parser.add_argument(
        "--source-file",
        type=str,
        default=DEFAULT_BR_HOLIDAYS_CLEAN_FILE,
        help="Brazil holidays cleaned source file name.",
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
        "Brazil holidays quality CLI started",
        extra={
            "clean_data_dir": str(args.clean_data_dir),
            "output_dir": str(args.output_dir),
            "source_file": args.source_file,
            "run_date": args.run_date,
        },
    )

    output_file = build_br_holidays_quality_checks(
        clean_data_dir=args.clean_data_dir,
        output_dir=args.output_dir,
        run_date=args.run_date,
        source_file=args.source_file,
    )

    logger.info(
        "Brazil holidays quality CLI completed successfully",
        extra={"output_file": str(output_file)},
    )


if __name__ == "__main__":
    main()