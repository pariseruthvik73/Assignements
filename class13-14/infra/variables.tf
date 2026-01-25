
variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}


variable "subnet_cidr" {
  type = list(string)
  default = [
    "10.1.0.0/24",
    "10.2.0.0/24",
    "10.3.0.0/24",
    "10.4.0.0/24",
    "10.5.0.0/24",
    "10.6.0.0/24",
  ]
}


variable "environment" {
  type = string
}

# 127.43.12.23

variable "app_name" {
  type    = string
  default = "candycush"
}

variable "DB_DEFAULT_SETTING" {
  type = map(string)

  default = {
    DB_NAME                   = "appdb"
    USERNAME                  = "my_admin"
    DB_ENGINE                 = "postgres"
    DB_ENGINE_VERSION         = "14.15"
    DB_INSTANCE_CLASS         = "db.t3.micro"
    DB_ALLOCATED_STORAGE      = "20"
    DB_CLUSTER_INSTANCE_COUNT = "2"
    DB_CLUSTER_INSTANCE_CLASS = "db.r5.large"
    DB_CLUSTER_ENGINE         = "aurora-postgresql"
    DB_CLUSTER_ENGINE_VERSION = "15.15"
  }
}