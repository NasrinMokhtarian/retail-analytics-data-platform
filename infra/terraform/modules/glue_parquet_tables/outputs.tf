output "table_names" {
  description = "Glue Parquet table names."
  value       = keys(aws_glue_catalog_table.this)
}