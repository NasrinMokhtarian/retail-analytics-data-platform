from __future__ import annotations

import argparse
import logging
from pathlib import Path

from retail_analytics.utils.logging import setup_logging
from retail_analytics.validation.report_gate import check_report_gate

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fail the pipeline if report files contain error-level failures."
    )

    parser.add_argument(
        "--report-path",
        nargs="+",
        required=True,
        help="One or more CSV report paths to validate.",
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

    logger.info(
        "Report gate checks started",
        extra={"report_count": len(args.report_path)},
    )

    for report_path_value in args.report_path:
        result = check_report_gate(Path(report_path_value))

        logger.info(
            "Report gate passed",
            extra={
                "report_path": str(result.report_path),
                "total_checks": result.total_checks,
                "passed_checks": result.passed_checks,
                "failed_checks": result.failed_checks,
                "warning_failures": result.warning_failures,
            },
        )

    logger.info("All report gates passed successfully")


if __name__ == "__main__":
    main()