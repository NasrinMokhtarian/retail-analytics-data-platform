variable "aws_region" {
  description = "AWS region where the Terraform state bucket will be created."
  type        = string
  default     = "eu-central-1"
}

variable "project_name" {
  description = "Project name used for naming and tagging."
  type        = string
  default     = "retail-analytics-data-platform"
}

variable "owner" {
  description = "Owner tag value."
  type        = string
  default     = "nasrin"
}

variable "environment" {
  description = "Bootstrap environment name."
  type        = string
  default     = "bootstrap"
}

variable "state_bucket_name" {
  description = "Globally unique S3 bucket name for Terraform remote state. Do not include secrets."
  type        = string
}