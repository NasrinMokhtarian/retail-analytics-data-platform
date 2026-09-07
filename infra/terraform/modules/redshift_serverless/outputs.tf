output "namespace_name" {
  description = "Redshift Serverless namespace name."
  value       = try(aws_redshiftserverless_namespace.this[0].namespace_name, null)
}

output "workgroup_name" {
  description = "Redshift Serverless workgroup name."
  value       = try(aws_redshiftserverless_workgroup.this[0].workgroup_name, null)
}

output "workgroup_arn" {
  description = "Redshift Serverless workgroup ARN."
  value       = try(aws_redshiftserverless_workgroup.this[0].arn, null)
}

output "admin_password_secret_arn" {
  description = "AWS-managed admin password secret ARN."
  value       = try(aws_redshiftserverless_namespace.this[0].admin_password_secret_arn, null)
  sensitive   = true
}

output "s3_access_role_arn" {
  description = "IAM role ARN used by Redshift to read the S3 Parquet layer."
  value       = try(aws_iam_role.redshift_s3_access[0].arn, null)
}