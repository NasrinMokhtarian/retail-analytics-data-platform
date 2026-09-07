# Athena CSV vs Parquet Optimization Proof

## Purpose

This report compares Athena scan statistics for the same processed datasets stored as CSV and Parquet.

## Method

- Query type: SELECT COUNT(*)
- CSV tables: base Glue tables
- Parquet tables: matching tables ending in _parquet
- Metric: Athena DataScannedInBytes from query execution statistics

## Results

| Metric | Value |
|---|---:|
| Tables compared | 11 |
| Passed comparisons | 9 |
| Warning comparisons | 2 |
| Failed comparisons | 0 |
| Total CSV scanned bytes | 208425387 |
| Total Parquet scanned bytes | 0 |
| Total scan reduction bytes | 208425387 |
| Total scan reduction percent | 100% |

## Notes

- This is a small project dataset, so the result should be presented as an optimization proof, not a large-scale benchmark.
- Row counts must match between CSV and Parquet tables.
- The comparison uses Athena query execution statistics, not estimated file sizes.
- Broader analytical queries may show different scan patterns depending on selected columns and filters.

## Detailed Report

CSV report:

G:\retail-analytics-data-platform\reports\aws_athena_optimization_proof\run_date=2026-06-16\athena_csv_vs_parquet_scan_comparison_report.csv
