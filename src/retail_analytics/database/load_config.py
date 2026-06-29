from dataclasses import dataclass
from pathlib import Path

from retail_analytics.cleaning.supplier_rules import SUPPLIER_CLEAN_OUTPUT_FILE
from retail_analytics.config import (
    OLIST_CLEAN_DATA_DIR,
    SUPPLIER_CLEAN_DATA_DIR,
    BR_HOLIDAYS_CLEAN_DATA_DIR,
    BR_HOLIDAYS_CLEAN_OUTPUT_FILE
)


@dataclass(frozen=True)
class PostgresLoadTarget:
    source_name: str
    source_run_date: str
    source_file: str
    cleaned_file_path: Path
    target_schema: str
    target_table: str

OLIST_LOAD_TARGETS: list[tuple[str, str]] = [
    ("customers_clean.csv", "olist_customers"),
    ("geolocation_clean.csv", "olist_geolocation"),
    ("order_items_clean.csv", "olist_order_items"),
    ("order_payments_clean.csv", "olist_order_payments"),
    ("order_reviews_clean.csv", "olist_order_reviews"),
    ("orders_clean.csv", "olist_orders"),
    ("products_clean.csv", "olist_products"),
    ("sellers_clean.csv", "olist_sellers"),
    ("product_category_translation_clean.csv", "product_category_translation"),
]
def build_olist_load_targets(olist_run_date: str) -> list[PostgresLoadTarget]:
    
    cleaned_run_dir = OLIST_CLEAN_DATA_DIR / f"run_date={olist_run_date}"
    return [
        PostgresLoadTarget(
            source_name="olist",
            source_run_date=olist_run_date,
            source_file=cleaned_file,
            cleaned_file_path=cleaned_run_dir / cleaned_file,
            target_schema="raw",
            target_table=target_table,
        )
        for cleaned_file, target_table in OLIST_LOAD_TARGETS
    ]

def build_supplier_load_targets(supplier_run_date: str) -> list[PostgresLoadTarget]:
    cleaned_run_dir = SUPPLIER_CLEAN_DATA_DIR / f"run_date={supplier_run_date}"

    return [
        PostgresLoadTarget(
            source_name="supplier",
            source_run_date=supplier_run_date,
            source_file=SUPPLIER_CLEAN_OUTPUT_FILE,
            cleaned_file_path=cleaned_run_dir / SUPPLIER_CLEAN_OUTPUT_FILE,
            target_schema="raw",
            target_table="supplier_product_updates",
        )
    ]
def build_br_holidays_load_targets(br_holidays_run_date: str)-> list[PostgresLoadTarget]:
 cleaned_run_dir = BR_HOLIDAYS_CLEAN_DATA_DIR / f"run_date={br_holidays_run_date}"

 return[
     PostgresLoadTarget(
            source_name="br_holidays",
            source_run_date=br_holidays_run_date,
            source_file=BR_HOLIDAYS_CLEAN_OUTPUT_FILE,
            cleaned_file_path=cleaned_run_dir / BR_HOLIDAYS_CLEAN_OUTPUT_FILE,
            target_schema="raw",
            target_table="br_holidays",
        )
 ]

def build_selected_load_targets(
    selected_sources: list[str],
    olist_run_date: str | None = None,
    supplier_run_date: str | None = None,
    br_holidays_run_date: str | None = None,
) -> list[PostgresLoadTarget]:
    load_targets: list[PostgresLoadTarget] = []

    if "olist" in selected_sources:
        if olist_run_date is None:
            raise ValueError("--olist-run-date is required when loading olist")
        load_targets.extend(build_olist_load_targets(olist_run_date))

    if "supplier" in selected_sources:
        if supplier_run_date is None:
            raise ValueError("--supplier-run-date is required when loading supplier")
        load_targets.extend(build_supplier_load_targets(supplier_run_date))

    if "br_holidays" in selected_sources:
        if br_holidays_run_date is None:
            raise ValueError("--br-holidays-run-date is required when loading br_holidays")
        load_targets.extend(build_br_holidays_load_targets(br_holidays_run_date))

    return load_targets


def validate_load_target_files_exist(load_targets: list[PostgresLoadTarget]) -> None:
    missing_files = [
        str(load_target.cleaned_file_path)
        for load_target in load_targets
        if not load_target.cleaned_file_path.exists()
    ]

    if missing_files:
        missing_files_text = "\n".join(missing_files)
        raise FileNotFoundError(
            "Some cleaned files required for PostgreSQL loading are missing:\n"
            f"{missing_files_text}"
        )