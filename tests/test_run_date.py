import pytest
from retail_analytics.validation.run_date import validate_run_date

def test_valid_run_date_accepts_valid_date() -> None:
    validate_run_date("2026-06-16")

@pytest.mark.parametrize(
    "invalid_run_date",
    [
    "2026/06/16",
    "16-06-2026",
    "2026-6-16",
    "2026-02-31",
    "not-a-date",
    "", 
    ]
)

def test_validate_run_date_rejects_invalid_format(invalid_run_date: str) -> None:
    with pytest.raises(ValueError):
        validate_run_date(invalid_run_date)