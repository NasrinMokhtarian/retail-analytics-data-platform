# Glue Catalog Module

## Purpose

This module creates the AWS Glue Data Catalog database used by Athena.

## Created Resources

- Glue Data Catalog database

## Not Included Yet

This module does not create:

- Glue tables
- Glue crawlers
- Glue ETL jobs
- Athena queries
- Redshift resources

## Design Note

The first implementation uses Terraform-defined catalog resources instead of Glue crawlers because the source files and schemas are known.