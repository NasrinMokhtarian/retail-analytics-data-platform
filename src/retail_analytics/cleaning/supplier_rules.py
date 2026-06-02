SUPPLIER_SOURCE_FILE = "supplier_product_updates_2026-05-24.csv"
SUPPLIER_CLEAN_OUTPUT_FILE = "supplier_product_updates_clean.csv"

ALLOWED_CURRENCIES = {"EUR", "USD"}
ALLOWED_STOCK_STATUSES = {"IN_STOCK","OUT_OF_STOCK","LIMITED","DISCONTINUED",}
TEXT_COLUMNS = [
    "supplier_id",
    "supplier_name",
    "product_id",
    "supplier_product_code",
    "updated_price",
    "currency",
    "stock_status",
    "valid_from",
    "last_updated_at",
    "comments",
]
BUSINESS_KEY_COLUMNS = [
    "supplier_id",
    "product_id",
    "supplier_product_code",
]