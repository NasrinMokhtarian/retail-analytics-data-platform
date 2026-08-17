variable "database_name" {
  description = "Glue database name."
  type        = string
}

variable "tables" {
  description = "CSV external table definitions."
  type = map(object({
    description = string
    s3_location = string
    columns = list(object({
      name = string
      type = string
    }))
  }))
}