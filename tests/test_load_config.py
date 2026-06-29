import pytest

from retail_analytics.database.load_config import build_selected_load_targets


def test_build_selected_load_targets_for_br_holidays_only() -> None:
    targets = build_selected_load_targets(
        selected_sources=["br_holidays"],
        br_holidays_run_date="2026-06-16",
    )

    assert len(targets) == 1

    target = targets[0]

    assert target.source_name == "br_holidays"
    assert target.source_run_date == "2026-06-16"
    assert target.source_file == "br_holidays_clean.csv"
    assert target.target_schema == "raw"
    assert target.target_table == "br_holidays"
    assert "run_date=2026-06-16" in str(target.cleaned_file_path)


def test_build_selected_load_targets_for_full_platform() -> None:
    targets = build_selected_load_targets(
        selected_sources=["olist", "supplier", "br_holidays"],
        olist_run_date="2026-05-26",
        supplier_run_date="2026-06-01",
        br_holidays_run_date="2026-06-16",
    )

    target_names = {(target.source_name, target.target_table) for target in targets}

    assert len(targets) == 11

    assert ("olist", "olist_customers") in target_names
    assert ("olist", "olist_orders") in target_names
    assert ("supplier", "supplier_product_updates") in target_names
    assert ("br_holidays", "br_holidays") in target_names


def test_build_selected_load_targets_requires_olist_run_date() -> None:
    with pytest.raises(ValueError, match="--olist-run-date"):
        build_selected_load_targets(selected_sources=["olist"])


def test_build_selected_load_targets_requires_supplier_run_date() -> None:
    with pytest.raises(ValueError, match="--supplier-run-date"):
        build_selected_load_targets(selected_sources=["supplier"])


def test_build_selected_load_targets_requires_br_holidays_run_date() -> None:
    with pytest.raises(ValueError, match="--br-holidays-run-date"):
        build_selected_load_targets(selected_sources=["br_holidays"])