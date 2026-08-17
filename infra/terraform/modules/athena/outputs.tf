output "workgroup_name" {
  description = "Name of the Athena workgroup."
  value       = aws_athena_workgroup.this.name
}

output "workgroup_id" {
  description = "ID of the Athena workgroup."
  value       = aws_athena_workgroup.this.id
}

output "query_result_location" {
  description = "S3 query result location used by the Athena workgroup."
  value       = var.query_result_location
}