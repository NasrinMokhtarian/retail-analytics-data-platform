import argparse
import logging
from datetime import date
from pathlib import Path

from retail_analytics.config import POSTGRES_VALIDATION_REPORT_DIR
from retail_analytics.database.postgres_validation import validate_postgres_loads
from retail_analytics.utils.logging import setup_logging
from retail_analytics.validation.run_date import validate_run_date

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate PostgreSQL raw table loads against cleaned files "
            "and audit records."
        )
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
        "--validation-run-date",
        type=str,
        default=date.today().isoformat(),
        help="Run date for the validation report in YYYY-MM-DD format.",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=POSTGRES_VALIDATION_REPORT_DIR,
        help="Directory where PostgreSQL validation reports will be written.",
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
    validate_run_date(args.validation_run_date)

    logger.info(
        "Validate PostgreSQL loads CLI started",
        extra={
            "selected_sources": args.only,
            "olist_run_date": args.olist_run_date,
            "supplier_run_date": args.supplier_run_date,
            "br_holidays_run_date": args.br_holidays_run_date,
            "validation_run_date": args.validation_run_date,
            "output_dir": str(args.output_dir),
        },
    )

    output_file = validate_postgres_loads(
        selected_sources=args.only,
        olist_run_date=args.olist_run_date,
        supplier_run_date=args.supplier_run_date,
        br_holidays_run_date=args.br_holidays_run_date,
        output_dir=args.output_dir,
        validation_run_date=args.validation_run_date,
    )

    logger.info(
        "Validate PostgreSQL loads CLI completed successfully",
        extra={"output_file": str(output_file)},
    )


if __name__ == "__main__":
    main()