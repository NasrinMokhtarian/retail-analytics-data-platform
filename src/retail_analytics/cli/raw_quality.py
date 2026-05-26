import argparse
import logging
from datetime import date
from pathlib import Path

from retail_analytics.config import RAW_QUALITY_REPORT_DIR,OLIST_DATA_DIR

from retail_analytics.quality.raw_quality import build_raw_quality_checks
from retail_analytics.utils.logging import setup_logging
from retail_analytics.validation.run_date import validate_run_date

logger = logging.getLogger(__name__)

def parse_args () -> argparse.Namespace:
    parser = argparse.ArgumentParser(description = "Run data quality check for Olist csv files")
    parser.add_argument("--raw-data-dir", type = Path, default= OLIST_DATA_DIR,help="Dictionary containing raw Olist csv files.")
    parser.add_argument("--output-dir", type = Path, default = RAW_QUALITY_REPORT_DIR, help = "Directory where the raw quality report will be written.")
    parser.add_argument("--run-date",type=str,default=date.today().isoformat(),help="Logical run date in YYYY-MM-DD format.")
    parser.add_argument("--log-level",type=str,default="INFO",choices=["DEBUG", "INFO", "WARNING", "ERROR"],help="Logging level.")

    return parser.parse_args()               

def main() -> None:
    args = parse_args()
    setup_logging(args.log_level)
    validate_run_date(args.run_date)
    logger.info("Raw quality CLI started!",
                extra={
                    "raw_data_dir": str(args.raw_data_dir),
                    "output_dir": str(args.output_dir),
                    "run_date": args.run_date,
                })
    output_file = build_raw_quality_checks(
        raw_data_dir= args.raw_data_dir,
        run_date= args.run_date,
        output_dir= args.output_dir
    )
    logger.info("Raw quality CLI completed successfully!",extra={"output_file": str(output_file)})

if __name__ == "__main__":
    main()