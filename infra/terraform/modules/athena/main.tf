resource "aws_athena_workgroup" "this" {
  name = var.workgroup_name

  configuration {
    enforce_workgroup_configuration = true

    result_configuration {
      output_location = var.query_result_location

      encryption_configuration {
        encryption_option = "SSE_S3"
      }
    }

    bytes_scanned_cutoff_per_query = var.bytes_scanned_cutoff_per_query
  }
}