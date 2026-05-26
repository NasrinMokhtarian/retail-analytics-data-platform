from dataclasses import dataclass

@dataclass(frozen=True)
class CleanedFileResult:
    source_file: str
    output_file: str
    row_count: int
    column_count: int
    timestamp_columns_processed: int
    numeric_column_processed: int
    invalid_timestamp_count:int
    invalid_numeric_count: int
    cleaned_at: str


