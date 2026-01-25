provider "aws" {
  region = "ap-south-1"
  default_tags {
    tags = {
      Environment = var.environment
      Owner       = "livingdevops@gmail.com"
      terraform   = "true"
      repo        = "nov25-bootcamp"
    }
  }

}