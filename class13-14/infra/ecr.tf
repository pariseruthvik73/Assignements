# resource "aws_ecr_repository" "python_app" {
#   name = "${var.environment}-${var.app_name}-flask"
# }
# resource "aws_ecr_repository" "redis" {
#   name = "${var.environment}-${var.app_name}-redis"
# }

# resource "aws_ecr_repository" "nginx" {
#   name = "${var.environment}-${var.app_name}-nginx"
# }


resource "aws_ecr_repository" "ecr" {
  for_each = local.ecs_services_interpreted
  name     = "${var.environment}-${var.app_name}-${each.key}"
}

# flask repo =  aws_ecr_repository.ecr["flask"]

# redis repo = aws_ecr_repository.ecr["redis"]

# nginx repo = aws_ecr_repository.ecr["nginx"]