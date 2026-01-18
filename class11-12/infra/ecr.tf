resource "aws_ecr_repository" "student_portal" {
  name                 = "student-portal"
  image_tag_mutability = "MUTABLE"

  tags = {
    Name = "student-portal"
  }
}

output "ecr_repository_url" {
  value       = aws_ecr_repository.student_portal.repository_url
  description = "The URL of the ECR repository"
}