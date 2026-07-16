# AWS Account Safety Checklist

## Purpose

This checklist documents the AWS account safety setup for the Retail Analytics Data Platform.

The goal is to prevent unexpected cloud costs and reduce security risk before creating project infrastructure.

This project uses AWS only after cost controls, access controls, and cleanup rules are clear.

---

## Safety Principle

No AWS data infrastructure should be created before the following are in place:

* root account protected with MFA
* billing and budget alerts enabled
* cost anomaly detection enabled
* least-privilege access plan documented
* no unnecessary long-term access keys
* clear destroy workflow for temporary resources

---

## Checklist

| Area             | Check                                             | Status      |
| ---------------- | ------------------------------------------------- | ----------- |
| Root account     | Root user MFA enabled                             | Done        |
| Root account     | Root access keys checked and removed if any exist | Done        |
| Billing          | Billing alerts enabled                            | Done        |
| Budget           | Monthly cost budget created                       | Done        |
| Budget           | Actual cost alert configured                      | Done        |
| Budget           | Forecasted cost alert configured                  | Done        |
| Cost monitoring  | Cost Anomaly Detection enabled                    | Done        |
| IAM              | Daily work does not use root user                 | Done        |
| IAM              | No unnecessary IAM access keys created            | Done        |
| IAM              | Terraform access approach documented before use   | Not started |
| Region           | Default project region selected                   | Done        |
| Tags             | Required project tags defined                     | Done        |
| Destroy workflow | Temporary resource cleanup principle documented   | Done        |

---

## Recommended Budget

Initial monthly budget target:

```text
5 EUR to 10 EUR
```

This is a safety target, not a guarantee of final AWS cost.

Recommended alerts:

| Alert type      | Threshold |
| --------------- | --------: |
| Actual cost     |       50% |
| Actual cost     |       80% |
| Actual cost     |      100% |
| Forecasted cost |      100% |

Example:

If the budget is 10 EUR:

| Alert             | Meaning                                        |
| ----------------- | ---------------------------------------------- |
| 5 EUR actual      | early warning                                  |
| 8 EUR actual      | strong warning                                 |
| 10 EUR actual     | budget reached                                 |
| 10 EUR forecasted | AWS predicts the monthly budget may be reached |

---

## Root User Safety

The AWS root user should be used only for account-level tasks.

Examples:

* account creation
* billing setup
* root MFA setup
* account recovery
* closing the account if ever needed

The root user should not be used for daily project work.

Root user safety checklist:

```text
enable MFA
use a strong unique password
do not create root access keys
delete root access keys if any exist
do not use root for Terraform
do not use root for AWS CLI
```

---

## IAM Access Principle

The project should follow least privilege.

That means every user, role, or policy should have only the permissions needed for the task.

For this project, the future Terraform access should only be able to manage the resources needed for the development environment.

Do not create broad long-term access keys until the Terraform access design is ready.

Preferred future direction:

```text
temporary credentials
IAM roles
AWS CLI SSO / IAM Identity Center if practical
limited Terraform permissions
```

Fallback for learning only:

```text
a dedicated IAM user with MFA and limited permissions
```

The fallback should be used only if the temporary-credential approach becomes too difficult for the learning phase.

---

## Project Region

Selected region:

```text
eu-central-1
```

Reason:

* EU region
* close to the Netherlands
* suitable for a European portfolio project
* common AWS region for data workloads

Alternative:

```text
eu-west-1
```

---

## Required Project Tags

Every Terraform-managed resource should include:

```text
Project = retail-analytics-data-platform
Environment = dev
Owner = nasrin
ManagedBy = terraform
CostControl = true
```

Optional component tags:

```text
Component = data-lake
Component = athena
Component = glue
Component = budget
Component = terraform-state
```

---

## Manual Console Actions

### 1. Enable root MFA

Status:

```text
Not started
```

Notes:

```text
Use AWS Console root account security settings.
Do not share MFA codes.
Do not use root user for daily work after setup.
```

### 2. Check root access keys

Status:

```text
Not started
```

Expected result:

```text
No root access keys exist.
```

If root access keys exist:

```text
delete them unless there is a very specific emergency reason to keep them.
```

### 3. Create AWS Budget

Status:

```text
Not started
```

Budget type:

```text
Cost budget
```

Budget period:

```text
Monthly
```

Recommended amount:

```text
5 EUR to 10 EUR
```

Recommended alerts:

```text
50% actual
80% actual
100% actual
100% forecasted
```

### 4. Enable Cost Anomaly Detection

Status:

```text
Not started
```

Recommended setup:

```text
Monitor type: AWS services
Alert type: email
Alert frequency: individual alerts or daily summary
```

### 5. Confirm billing email

Status:

```text
Not started
```

Expected result:

```text
Budget alerts and anomaly alerts go to an email address that is checked regularly.
```

---

## What Not To Do Yet

Do not create yet:

* Redshift Serverless
* Glue jobs
* Glue crawlers
* MWAA
* EC2 instances
* EMR clusters
* production IAM users
* broad Administrator access keys
* project S3 buckets manually

These will be introduced later through controlled Terraform steps.

---

## Definition of Done

Phase 8.2 is complete when:

```text
1. root MFA is enabled
2. root access keys are checked and removed if present
3. AWS Budget is created
4. budget alerts are configured
5. Cost Anomaly Detection is enabled
6. project region is confirmed
7. no project infrastructure has been created manually
8. this checklist is updated
9. this checklist is committed and pushed
```
