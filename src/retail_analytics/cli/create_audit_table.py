import argparse
import logging

from retail_analytics.database.audit_setup import (
    create_load_audit_table,
    verify_load_audit_table,
)
from retail_analytics.utils.logging import setup_logging


logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create PostgreSQL audit.load_audit table."
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

    logger.info("Create audit table CLI started")

    create_load_audit_table()
    verify_load_audit_table()

    logger.info("Create audit table CLI completed successfully")


if __name__ == "__main__":
    main()