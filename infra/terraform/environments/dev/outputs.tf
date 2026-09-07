output "aws_region" {
  description = "AWS region used by the dev Terraform environment."
  value       = var.aws_region
}

output "project_name" {
  description = "Project name used for tagging."
  value       = var.project_name
}

output "environment" {
  description = "Terraform environment name."
  value       = var.environment
}

output "data_lake_bucket_name" {
  description = "Name of the dev S3 data lake bucket."
  value       = module.s3_data_lake.bucket_name
}

output "data_lake_bucket_arn" {
  description = "ARN of the dev S3 data lake bucket."
  value       = module.s3_data_lake.bucket_arn
}

output "data_lake_prefixes" {
  description = "Top-level prefixes in the dev S3 data lake bucket."
  value       = module.s3_data_lake.prefixes
}

output "glue_database_name" {
  description = "Glue Data Catalog database name."
  value       = module.glue_catalog.database_name
}

output "glue_database_arn" {
  description = "Glue Data Catalog database ARN."
  value       = module.glue_catalog.database_arn
}

output "athena_workgroup_name" {
  description = "Athena workgroup name."
  value       = module.athena.workgroup_name
}

output "athena_query_result_location" {
  description = "Athena query result S3 location."
  value       = module.athena.query_result_location
}

output "processed_csv_glue_table_names" {
  description = "Glue table names for processed CSV sources."
  value       = module.processed_csv_glue_tables.table_names
}

output "processed_parquet_glue_table_names" {
  description = "Glue table names for processed Parquet sources."
  value       = module.processed_parquet_glue_tables.table_names
}

output "redshift_serverless_namespace_name" {
  description = "Redshift Serverless namespace name."
  value       = module.redshift_serverless.namespace_name
}

output "redshift_serverless_workgroup_name" {
  description = "Redshift Serverless workgroup name."
  value       = module.redshift_serverless.workgroup_name
}

output "redshift_serverless_workgroup_arn" {
  description = "Redshift Serverless workgroup ARN."
  value       = module.redshift_serverless.workgroup_arn
}

output "redshift_serverless_admin_password_secret_arn" {
  description = "AWS-managed Redshift admin password secret ARN."
  value       = module.redshift_serverless.admin_password_secret_arn
  sensitive   = true
}

output "redshift_serverless_s3_access_role_arn" {
  description = "IAM role ARN used by Redshift to read the S3 Parquet layer."
  value       = module.redshift_serverless.s3_access_role_arn
}