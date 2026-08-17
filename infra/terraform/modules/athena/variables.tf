variable "workgroup_name" {
  description = "Name of the Athena workgroup."
  type        = string
}

variable "query_result_location" {
  description = "S3 location where Athena query results are stored."
  type        = string
}

variable "bytes_scanned_cutoff_per_query" {
  description = "Optional maximum bytes scanned per query. Set to null to disable."
  type        = number
  default     = null
}