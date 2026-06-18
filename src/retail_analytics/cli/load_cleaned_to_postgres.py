import argparse
import logging

from retail_analytics.database.postgres_loader import load_cleaned_files_to_postgres
from retail_analytics.utils.logging import setup_logging
from retail_analytics.validation.run_date import validate_run_date


logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Load cleaned Olist,suppliers and br_holidays files into PostgreSQL raw tables."
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
        help="Run date for cleaned br holidays file in YYYY-MM-DD format.",
    )

    parser.add_argument(
    "--only",
    nargs="+",
    choices=["olist", "supplier", "br_holidays"],
    default=["olist", "supplier", "br_holidays"],
    help="Sources to load. Example: --only br_holidays",
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
    if args.olist_run_date is not None:
        validate_run_date(args.olist_run_date)
    if args.supplier_run_date is not None:
        validate_run_date(args.supplier_run_date)
    if args.br_holidays_run_date is not None:
        validate_run_date(args.br_holidays_run_date)

    logger.info(
        "Load cleaned files to PostgreSQL CLI started",
        extra={
            "olist_run_date": args.olist_run_date,
            "supplier_run_date": args.supplier_run_date,
            "br_holidays_run_date": args.br_holidays_run_date
        },
    )

    load_cleaned_files_to_postgres(
        olist_run_date=args.olist_run_date,
        supplier_run_date=args.supplier_run_date,
        br_holidays_run_date=args.br_holidays_run_date,
        selected_sources=args.only,
    )

    logger.info("Load cleaned files to PostgreSQL CLI completed successfully")


if __name__ == "__main__":
    main()