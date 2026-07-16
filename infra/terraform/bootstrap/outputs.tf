output "terraform_state_bucket_name" {
  description = "Name of the S3 bucket used for Terraform remote state."
  value       = aws_s3_bucket.terraform_state.bucket
}

output "terraform_state_bucket_arn" {
  description = "ARN of the S3 bucket used for Terraform remote state."
  value       = aws_s3_bucket.terraform_state.arn
}

output "terraform_state_region" {
  description = "AWS region where the Terraform state bucket is created."
  value       = var.aws_region
}

output "dev_backend_example" {
  description = "Example S3 backend configuration for the future dev environment."
  value = {
    bucket       = aws_s3_bucket.terraform_state.bucket
    key          = "retail-analytics/dev/terraform.tfstate"
    region       = var.aws_region
    encrypt      = true
    use_lockfile = true
  }
}