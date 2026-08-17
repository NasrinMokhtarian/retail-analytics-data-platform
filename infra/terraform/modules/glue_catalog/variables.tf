variable "database_name" {
  description = "Name of the Glue Data Catalog database."
  type        = string
}

variable "description" {
  description = "Description of the Glue Data Catalog database."
  type        = string
  default     = "Glue Data Catalog database for the Retail Analytics Data Platform processed zone."
}