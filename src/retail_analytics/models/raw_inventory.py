from dataclasses import dataclass

@dataclass(frozen=True)
class CSVFileInventory:
    file_name: str
    file_path: str
    row_count: int
    column_count: int
    columns: str
    file_size_mb: float
    inspected_at: str
