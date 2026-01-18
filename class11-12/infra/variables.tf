
variable "domain_name" {
  type    = string
  default = "akhileshmishra.tech"
}

variable "subdomain" {
  type    = string
  default = "class11"
}

variable "image" {
  type  = string
  default = "879381241087.dkr.ecr.ap-south-1.amazonaws.com/student-portal"
}

variable "tag" {
  type    = string
  default = "latest"
}

variable "container_port" {
  type    = number
  default = 8000
}
variable "health_check_path" {
  type    = string
  default = "/health"
}