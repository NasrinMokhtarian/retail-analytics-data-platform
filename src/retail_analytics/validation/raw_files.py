from pathlib import Path

def validate_row_data_dir(raw_data_path: Path) -> None:
    if not raw_data_path.exists():
        raise FileNotFoundError(f"Raw data directory does not exist: {raw_data_path} ")
    
    if not raw_data_path.is_dir():
        raise NotADirectoryError (f"Raw data path is not a directory: {raw_data_path}")
    
def validate_csv_file_exist(csv_files: list[Path],raw_data_path: Path) -> None:
    if not csv_files:
        raise FileNotFoundError(f" No csv Files found in {raw_data_path}."
                                "Please place the Olist scv files in data/raw/olist"
                                )

