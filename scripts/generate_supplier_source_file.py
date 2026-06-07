from pathlib import Path
import csv
from datetime import datetime


PROJECT_ROOT = Path(__file__).resolve().parents[1]

OUTPUT_DIR = PROJECT_ROOT / "data" / "raw" / "suppliers"
OUTPUT_FILE = OUTPUT_DIR / "supplier_product_updates_2026-05-24.csv"


SUPPLIER_ROWS = [
    {
        "supplier_id": "SUP001",
        "supplier_name": "  Alpha Home Supplies ",
        "product_id": "1e9e8ef04dbcff4541ed26657ea517e5",
        "supplier_product_code": " AH-1001 ",
        "updated_price": " 89.90 ",
        "currency": "EUR",
        "stock_status": "In Stock",
        "valid_from": "2026-05-24",
        "last_updated_at": "2026-05-24 09:15:00",
        "comments": "Normal update",
    },
    {
        "supplier_id": "SUP002",
        "supplier_name": "Beta Retail Group",
        "product_id": "3aa071139cb16b67ca9e5dea641aaa2f",
        "supplier_product_code": "BR-2201",
        "updated_price": "120,50",
        "currency": "eur",
        "stock_status": "in stock",
        "valid_from": "24-05-2026",
        "last_updated_at": "2026/05/24 10:30",
        "comments": "Price uses comma decimal separator",
    },
    {
        "supplier_id": "SUP003",
        "supplier_name": "Gamma Wholesale",
        "product_id": "",
        "supplier_product_code": "GW-3305",
        "updated_price": "45.00",
        "currency": "EUR",
        "stock_status": "Out of Stock",
        "valid_from": "2026-05-24",
        "last_updated_at": "2026-05-24 11:00:00",
        "comments": "Missing product_id",
    },
    {
        "supplier_id": "SUP004",
        "supplier_name": "Delta Imports",
        "product_id": "96bd76ec8810374ed1b65e291975717f",
        "supplier_product_code": "DI-4402",
        "updated_price": "not available",
        "currency": "EUR",
        "stock_status": "Limited",
        "valid_from": "2026-05-24",
        "last_updated_at": "2026-05-24 12:45:00",
        "comments": "Invalid price text",
    },
    {
        "supplier_id": "SUP005",
        "supplier_name": "Echo Distribution",
        "product_id": "cef67bcfe19066a932b7673e239eb23d",
        "supplier_product_code": "ED-5507",
        "updated_price": "-10.00",
        "currency": "EUR",
        "stock_status": "In Stock",
        "valid_from": "2026-05-24",
        "last_updated_at": "2026-05-24 13:05:00",
        "comments": "Negative price should be flagged",
    },
    {
        "supplier_id": "SUP006",
        "supplier_name": "Foxtrot Partner",
        "product_id": "9dc1a7de274444849c219cff195d0b71",
        "supplier_product_code": "FP-6609",
        "updated_price": "77.25",
        "currency": "USD",
        "stock_status": "In Stock",
        "valid_from": "2026-05-24",
        "last_updated_at": "invalid_date",
        "comments": "Unexpected currency and invalid timestamp",
    },
    {
        "supplier_id": "SUP007",
        "supplier_name": "  North Star Supply",
        "product_id": "41d3672d4792049fa1779bb35283ed13",
        "supplier_product_code": " NS-7701 ",
        "updated_price": "33.40",
        "currency": "EUR",
        "stock_status": "unknown",
        "valid_from": "2026-05-24",
        "last_updated_at": "2026-05-24 14:20:00",
        "comments": "Unknown stock status",
    },
    {
        "supplier_id": "SUP008",
        "supplier_name": "Orion Components",
        "product_id": "732bd381ad09e530fe0a5f457d81becb",
        "supplier_product_code": "OC-8800",
        "updated_price": "58.10",
        "currency": "",
        "stock_status": "In Stock",
        "valid_from": "",
        "last_updated_at": "2026-05-24 15:00:00",
        "comments": "Missing currency and valid_from",
    },
    {
        "supplier_id": "SUP008",
        "supplier_name": "Orion Components",
        "product_id": "732bd381ad09e530fe0a5f457d81becb",
        "supplier_product_code": "OC-8800",
        "updated_price": "58.10",
        "currency": "",
        "stock_status": "In Stock",
        "valid_from": "",
        "last_updated_at": "2026-05-24 15:00:00",
        "comments": "Duplicate row",
    },
    {
        "supplier_id": "SUP009",
        "supplier_name": "Zeta Market",
        "product_id": "2548af3e6e77a690cf3eb6368e9ab61e",
        "supplier_product_code": "ZM-9901",
        "updated_price": "102.99",
        "currency": "EUR",
        "stock_status": "Discontinued",
        "valid_from": "2026-05-24",
        "last_updated_at": "2026-05-24 16:10:00",
        "comments": "Valid discontinued product",
    },
]


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open(mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=SUPPLIER_ROWS[0].keys())
        writer.writeheader()
        writer.writerows(SUPPLIER_ROWS)

    print(f"Supplier source file created: {OUTPUT_FILE}")
    print(f"Rows written: {len(SUPPLIER_ROWS)}")


if __name__ == "__main__":
        main()