# AWS S3 Parquet Upload Runbook

## Purpose

This runbook documents how local Parquet outputs are uploaded to the S3 data lake.

## Cost Classification

This step is classified as:

```text
GREEN/YELLOW
```

## Reason:

No AWS compute is started.
No Terraform infrastructure is changed.
Cost comes from S3 storage and S3 requests only.
## Source

 Local Parquet root:

data/processed/parquet/
## Destination

 S3 prefix:

s3://retail-analytics-datalake-nasrin-dev-eu-central-1/processed/athena_parquet/
## Upload Script
scripts/upload_parquet_to_s3.ps1
## Dry Run
.\scripts\upload_parquet_to_s3.ps1 `
  -BucketName retail-analytics-datalake-nasrin-dev-eu-central-1 `
  -AwsProfile retail-analytics-dev `
  -LocalParquetRoot "data\processed\parquet" `
  -S3Prefix "processed/athena_parquet" `
  -UploadRunDate 2026-06-16 `
  -DryRun
## Real Upload
.\scripts\upload_parquet_to_s3.ps1 `
  -BucketName retail-analytics-datalake-nasrin-dev-eu-central-1 `
  -AwsProfile retail-analytics-dev `
  -LocalParquetRoot "data\processed\parquet" `
  -S3Prefix "processed/athena_parquet" `
  -UploadRunDate 2026-06-16
## Validation
aws s3 ls `
  s3://retail-analytics-datalake-nasrin-dev-eu-central-1/processed/athena_parquet/ `
  --recursive `
  --profile retail-analytics-dev
## Safety Rules
- Run dry run first.
- Do not use --delete.
- Do not run Terraform destroy.
- Do not delete S3 data unless explicitly planned.
- Keep CSV and Parquet layers separate.



