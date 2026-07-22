# S3 Data Lake Module

## Purpose

This module creates the S3 bucket used as the project data lake for the Retail Analytics Data Platform.

This bucket is separate from the Terraform state bucket.

## Created Resources

- S3 bucket
- bucket ownership controls
- public access block
- server-side encryption
- optional versioning
- top-level prefix placeholders

## Default Prefixes

```text
raw/
processed/
curated/
athena-results/
temp/