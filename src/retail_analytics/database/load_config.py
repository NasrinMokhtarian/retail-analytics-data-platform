from dataclasses import dataclass
from pathlib import Path

from retail_analytics.cleaning.supplier_rules import SUPPLIER_CLEAN_OUTPUT_FILE
from retail_analytics.config import (
    OLIST_CLEAN_DATA_DIR,
    SUPPLIER_CLEAN_DATA_DIR,
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
def build_all_load_targets(
    olist_run_date: str,
    supplier_run_date: str,
) -> list[PostgresLoadTarget]:
    return [
        *build_olist_load_targets(olist_run_date=olist_run_date),
        *build_supplier_load_targets(supplier_run_date=supplier_run_date),
    ]

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