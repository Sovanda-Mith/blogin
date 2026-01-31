# AWS Systems Manager Parameter Store

# Database password (sensitive)
resource "aws_ssm_parameter" "db_password" {
  name  = "/${local.name_prefix}/database/password"
  type  = "SecureString"
  value = var.db_password

  description = "Database password for ${local.name_prefix}"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-db-password"
  })
}

# Database username
resource "aws_ssm_parameter" "db_username" {
  name  = "/${local.name_prefix}/database/username"
  type  = "String"
  value = var.db_username

  description = "Database username for ${local.name_prefix}"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-db-username"
  })
}

# Database host
resource "aws_ssm_parameter" "db_host" {
  name  = "/${local.name_prefix}/database/host"
  type  = "String"
  value = aws_db_instance.main.address

  description = "Database host for ${local.name_prefix}"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-db-host"
  })
}

# Database name
resource "aws_ssm_parameter" "db_name" {
  name  = "/${local.name_prefix}/database/name"
  type  = "String"
  value = "blogin"

  description = "Database name for ${local.name_prefix}"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-db-name"
  })
}

# JWT Secret Key (sensitive)
resource "aws_ssm_parameter" "jwt_secret" {
  name  = "/${local.name_prefix}/jwt/secret"
  type  = "SecureString"
  value = var.jwt_secret_key

  description = "JWT secret key for ${local.name_prefix}"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-jwt-secret"
  })
}

# Service URLs for internal communication
resource "aws_ssm_parameter" "service_urls" {
  for_each = {
    auth_service    = "http://auth-service.${local.name_prefix}.local:8000"
    user_service    = "http://user-service.${local.name_prefix}.local:8000"
    post_service    = "http://post-service.${local.name_prefix}.local:8000"
    comment_service = "http://comment-service.${local.name_prefix}.local:8000"
    like_service    = "http://like-service.${local.name_prefix}.local:8000"
    gateway         = "http://gateway.${local.name_prefix}.local:8000"
  }

  name  = "/${local.name_prefix}/services/${replace(each.key, "_", "-")}/url"
  type  = "String"
  value = each.value

  description = "Service URL for ${each.key}"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-${each.key}-url"
  })
}

# S3 Avatar Bucket Name
resource "aws_ssm_parameter" "s3_avatar_bucket" {
  name  = "/${local.name_prefix}/s3/avatar-bucket"
  type  = "String"
  value = "${local.name_prefix}-avatars-${data.aws_caller_identity.current.account_id}"

  description = "S3 bucket name for user avatars"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-s3-avatar-bucket"
  })
}

# Output for SSM parameter ARNs
output "ssm_db_password_arn" {
  description = "SSM Parameter ARN for database password"
  value       = aws_ssm_parameter.db_password.arn
  sensitive   = true
}

output "ssm_jwt_secret_arn" {
  description = "SSM Parameter ARN for JWT secret"
  value       = aws_ssm_parameter.jwt_secret.arn
  sensitive   = true
}
