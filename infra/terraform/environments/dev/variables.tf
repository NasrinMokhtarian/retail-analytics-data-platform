variable "aws_region" {
  description = "AWS region for development resources."
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
  description = "Environment name."
  type        = string
  default     = "dev"
}

variable "data_lake_bucket_name" {
  description = "Globally unique S3 bucket name for the dev data lake."
  type        = string
}

variable "enable_data_lake_versioning" {
  description = "Whether to enable versioning on the dev data lake bucket."
  type        = bool
  default     = false
}