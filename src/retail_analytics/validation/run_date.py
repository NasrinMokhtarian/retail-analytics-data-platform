from datetime import datetime

def validate_run_date(run_date: str) -> None:
    try:
        datetime.strptime(run_date,"%Y-%m-%d")
       
    except ValueError as e:
        raise ValueError(
            f" invalid run_date '{run_date}'. Expected format:YYYY-MM-DD."
        )from e
    
