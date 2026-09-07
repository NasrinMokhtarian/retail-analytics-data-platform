variable "enable_redshift" {
  description = "Whether to create Redshift Serverless resources."
  type        = bool
  default     = false
}

variable "namespace_name" {
  description = "Redshift Serverless namespace name."
  type        = string
}

variable "workgroup_name" {
  description = "Redshift Serverless workgroup name."
  type        = string
}

variable "database_name" {
  description = "Initial Redshift database name."
  type        = string
}

variable "admin_username" {
  description = "Redshift admin username. Password is managed by AWS Secrets Manager."
  type        = string
}

variable "s3_bucket_name" {
  description = "S3 data lake bucket name that Redshift can read from."
  type        = string
}

variable "base_capacity" {
  description = "Base Redshift Serverless capacity in RPUs."
  type        = number
  default     = 4
}

variable "max_capacity" {
  description = "Maximum Redshift Serverless capacity in RPUs."
  type        = number
  default     = 4
}

variable "usage_limit_amount" {
  description = "Daily Redshift Serverless compute usage limit amount in RPU-hours."
  type        = number
  default     = 1
}

variable "usage_limit_period" {
  description = "Usage limit period."
  type        = string
  default     = "daily"
}

variable "publicly_accessible" {
  description = "Whether the Redshift Serverless workgroup is publicly accessible."
  type        = bool
  default     = false
}

variable "allowed_cidr_blocks" {
  description = "CIDR blocks allowed to connect to Redshift port 5439."
  type        = list(string)
  default     = []
}

variable "subnet_ids" {
  description = "Optional subnet IDs for Redshift Serverless. If empty, default VPC subnets are used when enabled."
  type        = list(string)
  default     = []
}

variable "tags" {
  description = "Tags to apply to Redshift resources."
  type        = map(string)
  default     = {}
}