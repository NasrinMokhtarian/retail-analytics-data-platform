variable "bucket_name" {
  description = "Globally unique S3 bucket name for the retail analytics data lake."
  type        = string
}

variable "enable_versioning" {
  description = "Whether to enable versioning on the data lake bucket."
  type        = bool
  default     = false
}

variable "prefixes" {
  description = "Top-level S3 prefixes to create as placeholder objects."
  type        = list(string)
  default = [
    "raw/",
    "processed/",
    "curated/",
    "athena-results/",
    "temp/"
  ]
}