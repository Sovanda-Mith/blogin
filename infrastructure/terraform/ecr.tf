# ECR Repositories

locals {
  services = [
    "auth-service",
    "user-service",
    "post-service",
    "comment-service",
    "like-service",
    "gateway",
    "frontend"
  ]
}

# ECR Repositories for all services
resource "aws_ecr_repository" "services" {
  for_each = toset(local.services)

  name                 = "${local.name_prefix}/${each.value}"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  force_delete = true

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-${each.value}"
  })
}

# Lifecycle policy to keep only the last 30 images
resource "aws_ecr_lifecycle_policy" "services" {
  for_each = aws_ecr_repository.services

  repository = each.value.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 30 images"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 30
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

# Outputs for ECR repository URLs
output "ecr_repository_urls" {
  description = "ECR repository URLs"
  value       = { for k, v in aws_ecr_repository.services : k => v.repository_url }
}

output "ecr_repository_arns" {
  description = "ECR repository ARNs"
  value       = { for k, v in aws_ecr_repository.services : k => v.arn }
}
