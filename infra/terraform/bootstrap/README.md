# Terraform Bootstrap

## Purpose

This Terraform layer creates the S3 bucket used for Terraform remote state.

It is administrative infrastructure, not a project data lake bucket.

## What This Layer Creates

- S3 bucket for Terraform state
- S3 bucket versioning
- S3 server-side encryption
- S3 public access block
- S3 ownership controls
- required project tags

## What This Layer Does Not Create

- project data lake bucket
- Athena workgroup
- Glue database
- Redshift
- Airflow AWS automation
- data upload jobs

## State Handling

This bootstrap layer is first run with temporary local Terraform state.

After the state bucket exists, the future `environments/dev` layer will use the S3 backend.

## Safety Rules

Do not use the AWS root user for Terraform.

Do not commit:

- `.terraform/`
- `terraform.tfstate`
- `terraform.tfstate.backup`
- `terraform.tfvars`
- AWS credentials
- account IDs if you do not want them public

## Local Validation

```powershell
terraform fmt -recursive
terraform init
terraform validate