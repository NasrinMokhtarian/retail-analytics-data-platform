import argparse
import logging
from retail_analytics.database.schema_setup import create_database_schemas, verify_database_schemas
from retail_analytics.utils.logging import setup_logging

logger = logging.getLogger(__name__)

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create PostgreSQL schemas for the Retail Analytics Data Platform."
    )

    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level.",
    )

    return parser.parse_args()



def main():
    args = parse_args()
    setup_logging(args.log_level)
    logger.info("Create PostgreSQL schemas CLI started")

    create_database_schemas()
    verify_database_schemas()
    logger.info("Create PostgreSQL schemas CLI completed successfully")


if __name__ == '__main__':
    main()