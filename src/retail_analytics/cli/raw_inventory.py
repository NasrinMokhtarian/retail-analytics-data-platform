import argparse
from datetime import datetime
from pathlib import Path
import logging

from retail_analytics.config import OLIST_DATA_DIR,RAW_INVENTORY_REPORT_DIR,DEFAULT_CHUNK_SIZE
from retail_analytics.ingestion.raw_inventory import build_raw_inventory
from retail_analytics.utils.logging import setup_logging
from retail_analytics.validation.run_date import validate_run_date


logger = logging.getLogger(__name__)

def parser_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser( description="Build raw inventory report from Olist files")
    parser.add_argument("--raw-data-dir", type =Path, default = OLIST_DATA_DIR)
    parser.add_argument("--output-dir", type = Path, default=RAW_INVENTORY_REPORT_DIR )
    parser.add_argument("--run-date", type =str, default=datetime.today().strftime("%Y-%m-%d"))
    parser.add_argument("--chunk-size", type =int , default= DEFAULT_CHUNK_SIZE)
    parser.add_argument("--log-level", type = str, default="INFO",choices= ["DEBUG","INFO","WARNING","ERROR"])

    return parser.parse_args()



def main() -> None:
    args = parser_args()
    setup_logging(args.log_level)

    validate_run_date(args.run_date)

    logger.info(
        "Raw inventory job started",
        extra={
            "raw_data_dir": str(args.raw_data_dir),
            "output_dir": str(args.output_dir),
            "run_date": args.run_date,
                },
        )
    output_file = build_raw_inventory(raw_data_dir = args.raw_data_dir,output_dir=args.output_dir,run_date= args.run_date,chunk_size= args.chunk_size)

    logger.info("Raw inventory job completed",
                extra={
                    "output_file":str(output_file)
                })
    

if __name__=="__main__":
    main()
