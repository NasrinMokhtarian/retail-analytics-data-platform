data "aws_vpc" "default" {
  count = var.enable_redshift ? 1 : 0

  default = true
}

data "aws_subnets" "default" {
  count = var.enable_redshift && length(var.subnet_ids) == 0 ? 1 : 0

  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default[0].id]
  }
}

data "aws_iam_policy_document" "redshift_assume_role" {
  count = var.enable_redshift ? 1 : 0

  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["redshift.amazonaws.com","redshift-serverless.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "redshift_s3_access" {
  count = var.enable_redshift ? 1 : 0

  name               = "${var.workgroup_name}-s3-access-role"
  assume_role_policy = data.aws_iam_policy_document.redshift_assume_role[0].json

  tags = var.tags
}

data "aws_iam_policy_document" "redshift_s3_read" {
  count = var.enable_redshift ? 1 : 0

  statement {
    sid = "ReadDataLakeBucket"

    actions = [
      "s3:GetBucketLocation",
      "s3:ListBucket"
    ]

    resources = [
      "arn:aws:s3:::${var.s3_bucket_name}"
    ]
  }

  statement {
    sid = "ReadDataLakeObjects"

    actions = [
      "s3:GetObject"
    ]

    resources = [
      "arn:aws:s3:::${var.s3_bucket_name}/processed/athena_parquet/*"
    ]
  }

  statement {
    sid = "ReadGlueCatalog"

    actions = [
      "glue:GetDatabase",
      "glue:GetDatabases",
      "glue:GetTable",
      "glue:GetTables",
      "glue:GetPartition",
      "glue:GetPartitions"
      ]

    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "redshift_s3_read" {
  count = var.enable_redshift ? 1 : 0

  name   = "${var.workgroup_name}-s3-read-policy"
  role   = aws_iam_role.redshift_s3_access[0].id
  policy = data.aws_iam_policy_document.redshift_s3_read[0].json
}

resource "aws_security_group" "redshift" {
  count = var.enable_redshift ? 1 : 0

  name        = "${var.workgroup_name}-sg"
  description = "Security group for temporary Redshift Serverless portfolio proof."
  vpc_id      = data.aws_vpc.default[0].id

  dynamic "ingress" {
    for_each = var.allowed_cidr_blocks

    content {
      description = "Allow Redshift access from approved CIDR."
      from_port   = 5439
      to_port     = 5439
      protocol    = "tcp"
      cidr_blocks = [ingress.value]
    }
  }

  egress {
    description = "Allow outbound traffic."
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = var.tags
}

resource "aws_redshiftserverless_namespace" "this" {
  count = var.enable_redshift ? 1 : 0

  namespace_name       = var.namespace_name
  db_name              = var.database_name
  admin_username       = var.admin_username
  manage_admin_password = true

  default_iam_role_arn = aws_iam_role.redshift_s3_access[0].arn
  iam_roles            = [aws_iam_role.redshift_s3_access[0].arn]

  log_exports = [
    "userlog",
    "connectionlog",
    "useractivitylog"
  ]

  tags = var.tags
}

resource "aws_redshiftserverless_workgroup" "this" {
  count = var.enable_redshift ? 1 : 0

  namespace_name = aws_redshiftserverless_namespace.this[0].namespace_name
  workgroup_name = var.workgroup_name

  base_capacity = var.base_capacity
  max_capacity  = var.max_capacity

  publicly_accessible = var.publicly_accessible

  subnet_ids = length(var.subnet_ids) > 0 ? var.subnet_ids : slice(data.aws_subnets.default[0].ids, 0, 3)

  security_group_ids = [
    aws_security_group.redshift[0].id
  ]

  config_parameter {
    parameter_key   = "require_ssl"
    parameter_value = "true"
  }

  config_parameter {
    parameter_key   = "enable_user_activity_logging"
    parameter_value = "true"
  }

  config_parameter {
    parameter_key   = "max_query_execution_time"
    parameter_value = "1800"
  }

  tags = var.tags
}

resource "aws_redshiftserverless_usage_limit" "compute_daily" {
  count = var.enable_redshift ? 1 : 0

  resource_arn  = aws_redshiftserverless_workgroup.this[0].arn
  usage_type    = "serverless-compute"
  amount        = var.usage_limit_amount
  period        = var.usage_limit_period
  breach_action = "deactivate"
}