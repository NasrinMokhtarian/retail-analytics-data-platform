# Redshift Serverless Enablement Plan

## Purpose

This document records the controlled plan for enabling Redshift Serverless for one short portfolio test window.

Redshift is used only for:

```text
S3 Parquet layer
→ Redshift Serverless
→ dbt Redshift models
→ Power BI connection proof
→ cleanup
```
## Cost Classification
RED

Reason:

Redshift Serverless can create compute charges in RPU-hours and storage charges.

## Local Enablement File
Redshift is enabled only with this local-only file:
```text 
infra/terraform/environments/dev/redshift_enablement.local.tfvars 
``` 
It contains:
```text 
enable_redshift = true

redshift_base_capacity       = 4
redshift_max_capacity        = 4
redshift_usage_limit_amount  = 1
redshift_publicly_accessible = true
redshift_allowed_cidr_blocks = ["<current-public-ip>/32"]
redshift_subnet_ids          = []
```

## Prepare Local Enablement Values
.\scripts\prepare_redshift_enablement_tfvars.ps1

## Disabled Safety Plan
terraform plan -var-file="terraform.tfvars"
## Enabled Preview Plan
``` command
    terraform plan `
  -var-file="terraform.tfvars" `
  -var-file="redshift_enablement.local.tfvars"
```
## Forbidden
Do not use 0.0.0.0/0.
Do not leave Redshift enabled.
Do not run terraform destroy for the whole dev environment.
Do not create unrelated compute services.

## Cleanup Rule

Cleanup must be Redshift-specific and reviewed before running.
The S3 data lake, Glue database, Athena workgroup, and Terraform state bucket should remain.