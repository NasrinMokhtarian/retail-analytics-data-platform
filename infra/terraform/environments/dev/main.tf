locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    Owner       = var.owner
    ManagedBy   = "terraform"
    CostControl = "true"
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