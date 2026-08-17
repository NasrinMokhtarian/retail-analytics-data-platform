output "table_names" {
  description = "Glue table names."
  value       = keys(aws_glue_catalog_table.this)
}

output "table_arns" {
  description = "Glue table ARNs."
  value = {
    for table_name, table in aws_glue_catalog_table.this :
    table_name => table.arn
  }
}