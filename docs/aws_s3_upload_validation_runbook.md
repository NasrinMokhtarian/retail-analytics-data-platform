# AWS S3 Upload Validation Runbook

## Purpose

This runbook documents how the project validates that cleaned local outputs were uploaded correctly to the AWS S3 data lake.

The validation compares local cleaned files against S3 objects by:

- source folder
- run date
- file count
- total bytes
- individual file existence
- individual file size

## Script

```text
scripts/validate_s3_uploads.ps1
```

## Command
```
.\scripts\validate_s3_uploads.ps1 `
  -BucketName <> `
  -AwsProfile retail-analytics-dev `
  -ValidationRunDate <> `
  -OlistRunDate <> `
  -SupplierRunDate <> `
  -BrHolidaysRunDate <>
  ```

## Output
reports/aws_s3_upload_validation/run_date=<>/s3_upload_validation_report.csv