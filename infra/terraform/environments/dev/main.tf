locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    Owner       = var.owner
    ManagedBy   = "terraform"
    CostControl = "true"
  }
  processed_csv_tables = {
    for table_name, table_definition in var.processed_csv_table_definitions :
    table_name => {
      description = table_definition.description
      s3_location = "s3://${module.s3_data_lake.bucket_name}/${table_definition.s3_prefix}"
      columns     = table_definition.columns
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = local.common_tags
  }
}

module "s3_data_lake" {
  source = "../../modules/s3_data_lake"

  bucket_name       = var.data_lake_bucket_name
  enable_versioning = var.enable_data_lake_versioning
}

module "glue_catalog" {
  source = "../../modules/glue_catalog"

  database_name = var.glue_database_name
  description   = "Processed-zone Glue Data Catalog database for the Retail Analytics Data Platform."
}

module "athena" {
  source = "../../modules/athena"

  workgroup_name                 = var.athena_workgroup_name
  query_result_location          = "s3://${module.s3_data_lake.bucket_name}/athena-results/"
  bytes_scanned_cutoff_per_query = var.athena_bytes_scanned_cutoff_per_query
}

module "processed_csv_glue_tables" {
  source = "../../modules/glue_csv_tables"

  database_name = module.glue_catalog.database_name
  tables        = local.processed_csv_tables
}