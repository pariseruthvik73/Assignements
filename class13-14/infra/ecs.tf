# ecs cluster (1)
resource "aws_ecs_cluster" "main" {
  name = "${var.environment}-${var.app_name}-cluster"
  service_connect_defaults {
    namespace = aws_service_discovery_http_namespace.main.arn
  }
}

resource "aws_service_discovery_http_namespace" "main" {
  name        = "${var.environment}-${var.app_name}-namespace"
  description = "ecs namesoace"
}

# ecs task definition (1 per service) -> total 3


# ecs service (1 per service) -> total 3