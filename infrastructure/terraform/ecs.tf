# ECS Cluster and Task Definitions

locals {
  service_configs = {
    "auth-service" = {
      cpu           = 256
      memory        = 512
      port          = 8000
      desired_count = 1
      environment = [
        { name = "DATABASE_URL", value = "postgresql://${var.db_username}:${var.db_password}@${aws_db_instance.main.address}:5432/blogin" },
        { name = "JWT_SECRET", value = var.jwt_secret_key },
        { name = "SERVICE_NAME", value = "auth-service" }
      ]
    }
    "user-service" = {
      cpu           = 256
      memory        = 512
      port          = 8000
      desired_count = 1
      environment = [
        { name = "DATABASE_URL", value = "postgresql://${var.db_username}:${var.db_password}@${aws_db_instance.main.address}:5432/blogin" },
        { name = "JWT_SECRET", value = var.jwt_secret_key },
        { name = "SERVICE_NAME", value = "user-service" },
        { name = "AWS_REGION", value = var.aws_region },
        { name = "S3_BUCKET_NAME", value = "${local.name_prefix}-avatars-${data.aws_caller_identity.current.account_id}" }
      ]
    }
    "post-service" = {
      cpu           = 256
      memory        = 512
      port          = 8000
      desired_count = 1
      environment = [
        { name = "DATABASE_URL", value = "postgresql://${var.db_username}:${var.db_password}@${aws_db_instance.main.address}:5432/blogin" },
        { name = "JWT_SECRET", value = var.jwt_secret_key },
        { name = "SERVICE_NAME", value = "post-service" }
      ]
    }
    "comment-service" = {
      cpu           = 256
      memory        = 512
      port          = 8000
      desired_count = 1
      environment = [
        { name = "DATABASE_URL", value = "postgresql://${var.db_username}:${var.db_password}@${aws_db_instance.main.address}:5432/blogin" },
        { name = "JWT_SECRET", value = var.jwt_secret_key },
        { name = "SERVICE_NAME", value = "comment-service" }
      ]
    }
    "like-service" = {
      cpu           = 256
      memory        = 512
      port          = 8000
      desired_count = 1
      environment = [
        { name = "DATABASE_URL", value = "postgresql://${var.db_username}:${var.db_password}@${aws_db_instance.main.address}:5432/blogin" },
        { name = "JWT_SECRET", value = var.jwt_secret_key },
        { name = "SERVICE_NAME", value = "like-service" }
      ]
    }
    "gateway" = {
      cpu           = 256
      memory        = 512
      port          = 8000
      desired_count = 1
      environment = [
        { name = "AUTH_SERVICE_URL", value = "http://auth-service.${local.name_prefix}.local:8000" },
        { name = "USER_SERVICE_URL", value = "http://user-service.${local.name_prefix}.local:8000" },
        { name = "POST_SERVICE_URL", value = "http://post-service.${local.name_prefix}.local:8000" },
        { name = "COMMENT_SERVICE_URL", value = "http://comment-service.${local.name_prefix}.local:8000" },
        { name = "LIKE_SERVICE_URL", value = "http://like-service.${local.name_prefix}.local:8000" },
        { name = "SERVICE_NAME", value = "gateway" }
      ]
    }
    "frontend" = {
      cpu           = 256
      memory        = 512
      port          = 80
      desired_count = 1
      environment = [
        { name = "API_GATEWAY_URL", value = "http://gateway.${local.name_prefix}.local:8000" },
        { name = "SERVICE_NAME", value = "frontend" }
      ]
    }
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "${local.name_prefix}-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-cluster"
  })
}

# ECS Cluster Capacity Providers
resource "aws_ecs_cluster_capacity_providers" "main" {
  cluster_name = aws_ecs_cluster.main.name

  capacity_providers = ["FARGATE", "FARGATE_SPOT"]

  default_capacity_provider_strategy {
    base              = 1
    weight            = 1
    capacity_provider = "FARGATE"
  }
}

# Task Definitions for each service
resource "aws_ecs_task_definition" "services" {
  for_each = local.service_configs

  family                   = "${local.name_prefix}-${each.key}"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = each.value.cpu
  memory                   = each.value.memory
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name      = each.key
      image     = "${aws_ecr_repository.services[each.key].repository_url}:latest"
      essential = true
      portMappings = [
        {
          containerPort = each.value.port
          protocol      = "tcp"
        }
      ]
      environment = each.value.environment
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.services[each.key].name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:${each.value.port}/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-${each.key}"
  })
}

# ECS Services
resource "aws_ecs_service" "services" {
  for_each = local.service_configs

  name            = each.key
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.services[each.key].arn
  desired_count   = each.value.desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }

  service_registries {
    registry_arn = aws_service_discovery_service.services[each.key].arn
  }

  dynamic "load_balancer" {
    for_each = each.key == "gateway" || each.key == "frontend" ? [1] : []
    content {
      target_group_arn = aws_lb_target_group.services[each.key].arn
      container_name   = each.key
      container_port   = each.value.port
    }
  }

  deployment_controller {
    type = "ECS"
  }

  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  propagate_tags = "SERVICE"

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-${each.key}"
  })

  depends_on = [aws_lb_listener.http]
}

# Service Discovery Namespace
resource "aws_service_discovery_private_dns_namespace" "main" {
  name        = "${local.name_prefix}.local"
  description = "Service discovery namespace for ${local.name_prefix}"
  vpc         = aws_vpc.main.id

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-namespace"
  })
}

# Service Discovery Services
resource "aws_service_discovery_service" "services" {
  for_each = local.service_configs

  name = each.key

  dns_config {
    namespace_id = aws_service_discovery_private_dns_namespace.main.id

    dns_records {
      ttl  = 10
      type = "A"
    }

    routing_policy = "MULTIVALUE"
  }

  health_check_custom_config {
    failure_threshold = 1
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-${each.key}"
  })
}

# Output for ECS cluster name
output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = aws_ecs_cluster.main.name
}

output "ecs_cluster_arn" {
  description = "ECS cluster ARN"
  value       = aws_ecs_cluster.main.arn
}
