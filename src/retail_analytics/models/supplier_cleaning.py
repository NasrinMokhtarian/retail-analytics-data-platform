from dataclasses import dataclass

@dataclass(frozen=True)
class SupplierCleaningResult:
    source_file: str
    output_file: str
    row_count: int
    column_count: int
    missing_product_id_count: int
    missing_currency_count: int
    invalid_price_count: int
    negative_price_count: int
    unknown_stock_status_count: int
    invalid_valid_from_count: int
    invalid_last_updated_at_count: int
    duplicate_business_key_count: int
    cleaned_at: str