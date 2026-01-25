data "aws_region" "current" {}

data "aws_availability_zones" "available" {
  state = "available"
}

output "zones" {
  value = data.aws_availability_zones.available.names[1]
}