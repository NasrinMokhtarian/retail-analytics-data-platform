from __future__ import annotations

import re
from datetime import datetime


RUN_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def validate_run_date(run_date: str) -> str:
    if not RUN_DATE_PATTERN.match(run_date):
        raise ValueError(
            "Invalid run_date format. Expected YYYY-MM-DD, "
            f"got: {run_date}"
        )

    try:
        datetime.strptime(run_date, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError(
            "Invalid run_date value. Expected a real calendar date in "
            f"YYYY-MM-DD format, got: {run_date}"
        ) from exc

    return run_date