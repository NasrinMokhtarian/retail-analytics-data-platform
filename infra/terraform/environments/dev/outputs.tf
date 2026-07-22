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