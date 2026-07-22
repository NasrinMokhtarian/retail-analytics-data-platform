# AWS S3 Upload Runbook

## Purpose

This runbook documents how cleaned local outputs are uploaded to the AWS S3 data lake for the Retail Analytics Data Platform.

The upload step moves already-cleaned and validated local files into the S3 `processed/` zone.

## Source

Local cleaned outputs:

```text
data/processed/
```

## Destination

S3 data lake bucket
## Safety Rules
- Run dry run first.
- Do not use --delete during early AWS testing.
- Upload only cleaned and validated outputs.
- Do not upload local secrets, Terraform state, .env, .venv, or raw credentials.
- Use the retail-analytics-dev AWS CLI profile.

## Dry Run Commands
```
aws s3 sync `
  .\data\processed\olist_clean\run_date=<> `
  s3://bucket url/processed/olist_clean/run_date=<>/ `
  --profile retail-analytics-dev `
  --dryrun

aws s3 sync `
  .\data\processed\supplier_clean\run_date=<> `
  s3://bucket url/processed/supplier_clean/run_date=<>/ `
  --profile retail-analytics-dev `
  --dryrun

aws s3 sync `
  .\data\processed\br_holidays_clean\run_date=<> `
  s3://bucket url/processed/br_holidays_clean/run_date=<>/ `
  --profile retail-analytics-dev `
  --dryrun
  ```

  ## Upload Commands
  ```
  aws s3 sync `
  .\data\processed\olist_clean\run_date=<> `
  s3://bucket url/processed/olist_clean/run_date=<>/ `
  --profile retail-analytics-dev

aws s3 sync `
  .\data\processed\supplier_clean\run_date=<> `
  s3://bucket url/processed/supplier_clean/run_date=<>/ `
  --profile retail-analytics-dev

aws s3 sync `
  .\data\processed\br_holidays_clean\run_date=<> `
 s3://bucket url/processed/br_holidays_clean/run_date=<>/ `
  --profile retail-analytics-dev
  ```

  ## Verification
  ```
  aws s3 ls `
  s3://bucket url/processed/ `
  --recursive `
  --profile retail-analytics-dev
  ```