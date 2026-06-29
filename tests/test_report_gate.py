import pandas as pd
import pytest

from retail_analytics.validation.report_gate import check_report_gate


def test_report_gate_passes_when_all_checks_pass(tmp_path) -> None:
    report_path = tmp_path / "quality_report.csv"

    pd.DataFrame(
        [
            {"status": "PASS", "severity": "error", "message": "ok"},
            {"status": "PASS", "severity": "warning", "message": "ok"},
        ]
    ).to_csv(report_path, index=False)

    result = check_report_gate(report_path)

    assert result.total_checks == 2
    assert result.passed_checks == 2
    assert result.failed_checks == 0
    assert result.error_failures == 0
    assert result.warning_failures == 0

def test_report_gate_allows_warning_failures(tmp_path) -> None:
    report_path = tmp_path / "quality_report.csv"

    pd.DataFrame(
        [
            {"status": "PASS", "severity": "error", "message": "ok"},
            {"status": "FAIL", "severity": "warning", "message": "warning only"},
        ]
    ).to_csv(report_path, index=False)

    result = check_report_gate(report_path)

    assert result.total_checks == 2
    assert result.passed_checks == 1
    assert result.failed_checks == 1
    assert result.error_failures == 0
    assert result.warning_failures == 1

def test_report_gate_fails_on_error_failure(tmp_path) -> None:
    report_path = tmp_path / "quality_report.csv"

    pd.DataFrame(
        [
            {
                "check_id": "CHECK_001",
                "status": "FAIL",
                "severity": "error",
                "failed_count": 1,
                "total_count": 10,
                "message": "bad data",
            }
        ]
    ).to_csv(report_path, index=False)

    with pytest.raises(RuntimeError, match="error-level failures"):
        check_report_gate(report_path)


def test_report_gate_requires_status_and_severity_columns(tmp_path) -> None:
    report_path = tmp_path / "quality_report.csv"

    pd.DataFrame(
        [
            {"status": "PASS", "message": "missing severity"},
        ]
    ).to_csv(report_path, index=False)

    with pytest.raises(ValueError):
        check_report_gate(report_path)