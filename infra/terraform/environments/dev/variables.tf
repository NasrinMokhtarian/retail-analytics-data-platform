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

variable "glue_database_name" {
  description = "Glue Data Catalog database name for processed data."
  type        = string
  default     = "retail_analytics_processed_dev"
}

variable "athena_workgroup_name" {
  description = "Athena workgroup name for the dev environment."
  type        = string
  default     = "retail_analytics_dev"
}

variable "athena_bytes_scanned_cutoff_per_query" {
  description = "Optional maximum bytes scanned per Athena query."
  type        = number
  default     = 104857600
}

variable "processed_csv_table_definitions" {
  description = "Processed CSV Glue/Athena table definitions."
  type = map(object({
    description = string
    s3_prefix   = string
    columns = list(object({
      name = string
      type = string
    }))
  }))
  default = {}
}

variable "processed_parquet_table_definitions" {
  description = "Processed Parquet Glue/Athena table definitions."
  type = map(object({
    description = string
    s3_prefix   = string
    columns = list(object({
      name = string
      type = string
    }))
  }))
  default = {}
}

variable "enable_redshift" {
  description = "Whether to create Redshift Serverless resources."
  type        = bool
  default     = false
}

variable "redshift_base_capacity" {
  description = "Redshift Serverless base capacity in RPUs."
  type        = number
  default     = 4
}

variable "redshift_max_capacity" {
  description = "Redshift Serverless max capacity in RPUs."
  type        = number
  default     = 4
}

variable "redshift_usage_limit_amount" {
  description = "Daily Redshift Serverless usage limit in RPU-hours."
  type        = number
  default     = 1
}

variable "redshift_publicly_accessible" {
  description = "Whether Redshift Serverless should be publicly accessible."
  type        = bool
  default     = false
}

variable "redshift_allowed_cidr_blocks" {
  description = "Approved CIDR blocks allowed to connect to Redshift."
  type        = list(string)
  default     = []
}

variable "redshift_subnet_ids" {
  description = "Optional subnet IDs for Redshift Serverless."
  type        = list(string)
  default     = []
}