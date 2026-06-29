import argparse
import logging
from dataclasses import asdict

from retail_analytics.database.load_config import (
    build_selected_load_targets,
    validate_load_target_files_exist,
)
from retail_analytics.utils.logging import setup_logging
from retail_analytics.validation.run_date import validate_run_date

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate cleaned file mappings before PostgreSQL loading."
    )

    parser.add_argument(
        "--olist-run-date",
        type=str,
        required=False,
        help="Run date for cleaned Olist files in YYYY-MM-DD format.",
    )

    parser.add_argument(
        "--supplier-run-date",
        type=str,
        required=False,
        help="Run date for cleaned supplier file in YYYY-MM-DD format.",
    )

    parser.add_argument(
        "--br-holidays-run-date",
        type=str,
        required=False,
        help="Run date for cleaned Brazil holidays file in YYYY-MM-DD format.",
    )

    parser.add_argument(
        "--only",
        nargs="+",
        choices=["olist", "supplier", "br_holidays"],
        default=["olist", "supplier", "br_holidays"],
        help="Sources to validate. Example: --only br_holidays",
    )

    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level.",
    )

    return parser.parse_args()


def validate_optional_run_date(run_date: str | None) -> None:
    if run_date is not None:
        validate_run_date(run_date)


def main() -> None:
    args = parse_args()

    setup_logging(args.log_level)

    validate_optional_run_date(args.olist_run_date)
    validate_optional_run_date(args.supplier_run_date)
    validate_optional_run_date(args.br_holidays_run_date)

    logger.info(
        "PostgreSQL load configuration validation started",
        extra={
            "selected_sources": args.only,
            "olist_run_date": args.olist_run_date,
            "supplier_run_date": args.supplier_run_date,
            "br_holidays_run_date": args.br_holidays_run_date,
        },
    )

    load_targets = build_selected_load_targets(
        selected_sources=args.only,
        olist_run_date=args.olist_run_date,
        supplier_run_date=args.supplier_run_date,
        br_holidays_run_date=args.br_holidays_run_date,
    )

    validate_load_target_files_exist(load_targets)

    for load_target in load_targets:
        logger.info(
            "PostgreSQL load target validated",
            extra=asdict(load_target),
        )

    logger.info(
        "PostgreSQL load configuration validation completed successfully",
        extra={"load_target_count": len(load_targets)},
    )


if __name__ == "__main__":
    main()