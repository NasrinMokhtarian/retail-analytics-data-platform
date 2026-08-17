# Athena Module

## Purpose

This module creates the Athena workgroup used to query the S3 data lake.

## Created Resources

- Athena workgroup
- Athena query result output location configuration
- SSE-S3 encryption for query results
- optional bytes-scanned cutoff per query

## Not Included Yet

This module does not create:

- Glue tables
- Athena named queries
- dbt integration
- Redshift resources

## Design Note

The workgroup stores query results in the project S3 data lake under:

```text
athena-results/
```