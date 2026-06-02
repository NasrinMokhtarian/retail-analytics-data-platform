import argparse
from datetime import datetime
from pathlib import Path
import logging
from retail_analytics.config import SUPPLIER_RAW_DATA_DIR,SUPPLIER_INVENTORY_REPORT_DIR,DEFAULT_CHUNK_SIZE
from retail_analytics.ingestion.raw_inventory import build_raw_inventory
from retail_analytics.utils.logging import setup_logging
from retail_analytics.validation.run_date import validate_run_date

logger = logging.getLogger(__name__)

def parser_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser( description="Build supplier source inventory report ")
    parser.add_argument("--raw-data-dir", type =Path, default = SUPPLIER_RAW_DATA_DIR, help="Directory containing raw supplier files.")
    parser.add_argument("--output-dir", type = Path, default=SUPPLIER_INVENTORY_REPORT_DIR,help="Directory where the supplier inventory report will be written." )
    parser.add_argument("--run-date", type =str, default=datetime.today().strftime("%Y-%m-%d"),help="Logical run date in YYYY-MM-DD format.")
    parser.add_argument("--chunk-size", type =int , default= DEFAULT_CHUNK_SIZE,help="Chunk size used when counting CSV rows.")
    parser.add_argument("--log-level", type = str, default="INFO",choices= ["DEBUG","INFO","WARNING","ERROR"], help="Logging level.")

    return parser.parse_args()


def main() -> None:
    args = parser_args()
    setup_logging(args.log_level)

    validate_run_date(args.run_date)

    logger.info(
        "Supplier inventory CLI started",
        extra={
            "raw_data_dir": str(args.raw_data_dir),
            "output_dir": str(args.output_dir),
            "run_date": args.run_date,
                },
        )
    output_file = build_raw_inventory(raw_data_dir = args.raw_data_dir,output_dir=args.output_dir,run_date= args.run_date,chunk_size= args.chunk_size,output_filename="supplier_file_inventory.csv",)

    logger.info("Supplier inventory CLI completed",
                extra={
                    "output_file":str(output_file)
                })
    
if __name__ == "__main__":
    main()
    