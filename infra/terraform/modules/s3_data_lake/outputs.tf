output "bucket_name" {
  description = "Name of the S3 data lake bucket."
  value       = aws_s3_bucket.this.bucket
}

output "bucket_arn" {
  description = "ARN of the S3 data lake bucket."
  value       = aws_s3_bucket.this.arn
}

output "prefixes" {
  description = "Top-level prefixes created in the data lake bucket."
  value       = var.prefixes
}