from __future__ import annotations

import argparse

from retail_analytics.database.pipeline_audit import (
    finish_pipeline_run,
    start_pipeline_run,
)
from retail_analytics.validation.run_date import validate_run_date


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create and update pipeline-level audit records."
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    start_parser = subparsers.add_parser(
        "start",
        help="Start a new pipeline run audit record.",
    )
    start_parser.add_argument(
        "--pipeline-name",
        required=True,
        help="Pipeline name.",
    )
    start_parser.add_argument(
        "--run-date",
        required=True,
        help="Pipeline run date in YYYY-MM-DD format.",
    )
    start_parser.add_argument(
        "--selected-source",
        nargs="+",
        required=False,
        help="Selected source names included in this pipeline run.",
    )

    finish_parser = subparsers.add_parser(
        "finish",
        help="Finish an existing pipeline run audit record.",
    )
    finish_parser.add_argument(
        "--pipeline-run-id",
        required=True,
        type=int,
        help="Pipeline run ID returned by the start command.",
    )
    finish_parser.add_argument(
        "--status",
        required=True,
        choices=["SUCCESS", "FAILED"],
        help="Final pipeline run status.",
    )
    finish_parser.add_argument(
        "--error-message",
        required=False,
        help="Error message when the pipeline failed.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.command == "start":
        validate_run_date(args.run_date)

        pipeline_run_id = start_pipeline_run(
            pipeline_name=args.pipeline_name,
            run_date=args.run_date,
            selected_sources=args.selected_source,
        )

        print(pipeline_run_id)

    elif args.command == "finish":
        finish_pipeline_run(
            pipeline_run_id=args.pipeline_run_id,
            status=args.status,
            error_message=args.error_message,
        )


if __name__ == "__main__":
    main()