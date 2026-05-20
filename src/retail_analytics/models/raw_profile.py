from dataclasses import dataclass

@dataclass
class RawColumnProfile:
    file_name: str
    column_name: str
    column_dtype: str
    row_count: int
    null_count: int
    null_percentage: int
    non_null_count: int
    distinct_count: int
    sample_values: str
    profiled_at: str