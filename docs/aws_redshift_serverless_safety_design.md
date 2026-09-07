# AWS Redshift Serverless Safety Design

## Purpose

This document defines the safety design for using Amazon Redshift Serverless in the Retail Analytics Data Platform.

Redshift Serverless is used only as a temporary portfolio proof layer:

```text
S3 Parquet data lake
→ Redshift warehouse
→ dbt transformations
→ Power BI report connection
→ cleanup
```
## Step 2 — Create Redshift operating checklist
# AWS Redshift Serverless Operating Checklist

## Before Creation

Confirm:

```text
[ ] I intentionally want to create Redshift Serverless now.
[ ] I understand this is a RED-cost phase.
[ ] I have reviewed the Terraform plan.
[ ] The plan creates only expected Redshift-related resources.
[ ] The plan does not destroy unrelated resources.
[ ] A usage limit is included.
[ ] Cleanup instructions are ready before apply.
```
## During Use
Allowed activities:

[ ] Validate connectivity.
[ ] Create/load small portfolio tables.
[ ] Run dbt models.
[ ] Connect Power BI.
[ ] Capture screenshots and documentation evidence.

Avoid:
[ ] Long idle sessions.
[ ] Repeated experimental queries.
[ ] Full table scans unless needed.
[ ] Leaving Power BI open and refreshing repeatedly.

## After Use
 Confirm:

[ ] Redshift proof is complete.
[ ] Screenshots/evidence are saved.
[ ] dbt result is documented.
[ ] Power BI connection is documented.
[ ] Redshift resources are deleted.
[ ] AWS console confirms no Redshift Serverless workgroup remains.


