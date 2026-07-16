# AWS Terraform Access Design

## Purpose

This document defines how Terraform should access AWS for the Retail Analytics Data Platform.

The goal is to avoid root access, avoid unnecessary long-term access keys, and use a safer authentication method for local Terraform development.

---

## Access Principle

Terraform must not use the AWS root user.

Terraform should use:

```text
Preferred for enterprise: IAM Identity Center organization instance / AWS CLI SSO
Chosen for this personal portfolio account: dedicated IAM user with limited permissions
→ temporary credentials
→ named AWS CLI profile
→ Terraform AWS provider
```

This keeps authentication safer than using long-term access keys.

---

## Why Not Root Access

The AWS root user is for account-level tasks only.

Root should be used for:

* account setup
* billing setup
* MFA setup
* recovery tasks

Root should not be used for:

* Terraform
* AWS CLI
* daily project work
* data engineering development

Root access keys should not be created.

---

## Preferred Access Method

Preferred method:

```text
AWS IAM Identity Center
```

Reason:

* supports temporary credentials
* avoids long-term access keys
* works with AWS CLI profiles
* works with Terraform through the AWS provider
* follows modern AWS access best practices

---

## Local CLI Profile

Recommended profile name:

```text
retail-analytics-dev
```

Terraform commands should be run using this profile.

Example future command:

```powershell
$env:AWS_PROFILE = "retail-analytics-dev"
terraform plan -var-file="terraform.tfvars"
```

---

## Initial Permission Scope

For the bootstrap apply, Terraform only needs permission to create and configure the Terraform state S3 bucket.

Needed service area:

```text
S3
```

Bootstrap resources:

* S3 bucket
* S3 bucket versioning
* S3 server-side encryption configuration
* S3 public access block
* S3 ownership controls
* bucket tags

This access should be kept limited where practical.

---

## Future Permission Scope

Later phases may require permissions for:

* S3 data lake bucket
* Glue database and tables
* Athena workgroup
* AWS Budgets
* IAM policies or roles

Those permissions should be added only when the corresponding Terraform module is implemented.

---

## What Not To Do

Do not:

* create root access keys
* commit AWS credentials
* store access keys in Terraform files
* store access keys in `.env`
* use AdministratorAccess longer than necessary
* create project resources manually in the AWS Console

---

## Credential Files

AWS CLI may store profile configuration locally under the user profile directory.

These files are local machine configuration and should not be committed:

```text
~/.aws/config
~/.aws/credentials
```

The project repository should contain only example configuration, not real credentials.

---

## Terraform Provider Usage

The Terraform AWS provider should rely on the active AWS CLI profile or environment variables.

Do not hardcode credentials in provider blocks.

Example:

```hcl
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = local.common_tags
  }
}
```

---

## Validation Commands

After AWS CLI SSO is configured, validate identity with:

```powershell
aws sts get-caller-identity --profile retail-analytics-dev
```

This command should show the authenticated identity.

Do not paste account IDs or sensitive details into public documentation.

---

## Bootstrap Apply Command

After safe access is configured and validated, the bootstrap apply can be run from:

```text
infra/terraform/bootstrap/
```

Using:

```powershell
$env:AWS_PROFILE = "retail-analytics-dev"

terraform plan -var-file="terraform.tfvars"
terraform apply -var-file="terraform.tfvars"
```

---

## Definition of Done

Phase 8.5 is complete when:

```text
1. Terraform access method is documented
2. root user is not used for Terraform
3. no root access keys exist
4. AWS CLI profile is configured
5. AWS CLI profile uses temporary credentials where possible
6. aws sts get-caller-identity works
7. no credentials are committed
8. access design document is committed and pushed
```
## Chosen Access Method for This Project

IAM Identity Center was evaluated first because it is the preferred modern access pattern for temporary credentials.

During setup, the available IAM Identity Center experience did not expose the expected AWS account assignment and permission-set workflow for this personal portfolio account.

For this reason, the project uses a controlled fallback:

```text
Dedicated IAM user
→ limited bootstrap S3 policy
→ local AWS CLI named profile
→ Terraform uses the named profile