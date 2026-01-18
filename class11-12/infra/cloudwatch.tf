resource "aws_cloudwatch_log_group" "ecs_logs" {
  name              = "/ecs/student-portal"
  retention_in_days = 7
}