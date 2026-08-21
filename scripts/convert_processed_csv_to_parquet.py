from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from pyspark.sql import SparkSession
from pyspark.sql.types import StringType, StructField, StructType


@dataclass(frozen=True)
class SourceGroup:
    source_name: str
    run_date: str
    input_dir: Path


def normalize_table_name(file_path: Path, source_name: str) -> str:
    stem = file_path.stem

    if stem.endswith("_clean"):
        stem = stem[: -len("_clean")]

    if source_name == "olist":
        return f"olist_{stem}"

    return stem


def normalize_column_name(name: str) -> str:
    clean = name.strip().lower()

    normalized_chars = []
    previous_was_underscore = False

    for char in clean:
        if char.isalnum() or char == "_":
            normalized_chars.append(char)
            previous_was_underscore = False
        else:
            if not previous_was_underscore:
                normalized_chars.append("_")
                previous_was_underscore = True

    normalized = "".join(normalized_chars).strip("_")

    if normalized and normalized[0].isdigit():
        normalized = f"col_{normalized}"

    if not normalized:
        raise ValueError(f"Column name became empty after normalization: {name!r}")

    return normalized


def read_csv_header(file_path: Path) -> list[str]:
    with file_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration as exc:
            raise ValueError(f"CSV file is empty: {file_path}") from exc

    if not header:
        raise ValueError(f"CSV file has no header: {file_path}")

    normalized = [normalize_column_name(column) for column in header]

    if len(set(normalized)) != len(normalized):
        raise ValueError(
            f"Duplicate normalized columns found in {file_path}: {normalized}"
        )

    return normalized


def build_all_string_schema(columns: Iterable[str]) -> StructType:
    return StructType(
        [StructField(column_name, StringType(), True) for column_name in columns]
    )


def convert_file_to_parquet(
    spark: SparkSession,
    csv_file: Path,
    output_root: Path,
    source_name: str,
    run_date: str,
) -> dict[str, object]:
    table_name = normalize_table_name(csv_file, source_name)
    columns = read_csv_header(csv_file)
    schema = build_all_string_schema(columns)

    output_path = output_root / table_name / f"run_date={run_date}"

    df = (
        spark.read.option("header", "true")
        .option("multiLine", "true")
        .option("escape", '"')
        .option("quote", '"')
        .schema(schema)
        .csv(str(csv_file))
    )

    row_count = df.count()
    column_count = len(df.columns)

    (
        df.coalesce(1)
        .write.mode("overwrite")
        .option("compression", "snappy")
        .parquet(str(output_path))
    )

    return {
        "source_name": source_name,
        "table_name": table_name,
        "run_date": run_date,
        "input_file": str(csv_file),
        "output_path": str(output_path),
        "row_count": row_count,
        "column_count": column_count,
        "status": "PASS",
    }


def write_report(rows: list[dict[str, object]], report_path: Path) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "source_name",
        "table_name",
        "run_date",
        "input_file",
        "output_path",
        "row_count",
        "column_count",
        "status",
        "error_message",
    ]

    with report_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            complete_row = {field: row.get(field, "") for field in fieldnames}
            writer.writerow(complete_row)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert cleaned processed CSV outputs to local Parquet files."
    )

    parser.add_argument("--project-root", default=".", help="Project root directory.")
    parser.add_argument("--olist-run-date", required=True)
    parser.add_argument("--supplier-run-date", required=True)
    parser.add_argument("--br-holidays-run-date", required=True)
    parser.add_argument("--conversion-run-date", required=True)

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    project_root = Path(args.project_root).resolve()

    source_groups = [
        SourceGroup(
            source_name="olist",
            run_date=args.olist_run_date,
            input_dir=project_root
            / "data"
            / "processed"
            / "olist_clean"
            / f"run_date={args.olist_run_date}",
        ),
        SourceGroup(
            source_name="supplier",
            run_date=args.supplier_run_date,
            input_dir=project_root
            / "data"
            / "processed"
            / "supplier_clean"
            / f"run_date={args.supplier_run_date}",
        ),
        SourceGroup(
            source_name="br_holidays",
            run_date=args.br_holidays_run_date,
            input_dir=project_root
            / "data"
            / "processed"
            / "br_holidays_clean"
            / f"run_date={args.br_holidays_run_date}",
        ),
    ]

    output_root = project_root / "data" / "processed" / "parquet"
    report_path = (
        project_root
        / "reports"
        / "parquet_conversion"
        / f"run_date={args.conversion_run_date}"
        / "parquet_conversion_report.csv"
    )

    spark = (
        SparkSession.builder.appName("retail-analytics-local-parquet-conversion")
        .master("local[*]")
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )

    rows: list[dict[str, object]] = []

    try:
        for source_group in source_groups:
            if not source_group.input_dir.exists():
                raise FileNotFoundError(
                    f"Input folder does not exist: {source_group.input_dir}"
                )

            csv_files = sorted(source_group.input_dir.glob("*.csv"))

            if not csv_files:
                raise FileNotFoundError(
                    f"No CSV files found in: {source_group.input_dir}"
                )

            for csv_file in csv_files:
                print(f"Converting {csv_file}")

                try:
                    result = convert_file_to_parquet(
                        spark=spark,
                        csv_file=csv_file,
                        output_root=output_root,
                        source_name=source_group.source_name,
                        run_date=source_group.run_date,
                    )
                    rows.append(result)
                    print(
                        "  PASS "
                        f"table={result['table_name']} "
                        f"rows={result['row_count']} "
                        f"columns={result['column_count']}"
                    )
                except Exception as exc:
                    rows.append(
                        {
                            "source_name": source_group.source_name,
                            "table_name": normalize_table_name(
                                csv_file, source_group.source_name
                            ),
                            "run_date": source_group.run_date,
                            "input_file": str(csv_file),
                            "output_path": "",
                            "row_count": "",
                            "column_count": "",
                            "status": "FAIL",
                            "error_message": str(exc),
                        }
                    )
                    raise

    finally:
        write_report(rows, report_path)
        spark.stop()

    print()
    print(f"Parquet conversion report written to: {report_path}")

    failures = [row for row in rows if row.get("status") == "FAIL"]
    if failures:
        raise RuntimeError(f"Parquet conversion failed for {len(failures)} file(s).")

    print(f"Converted {len(rows)} CSV file(s) to Parquet successfully.")


if __name__ == "__main__":
    main()