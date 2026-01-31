locals {

  # list -> [1,2,3,4,5,7,8,34,5] -> set(list)  -> {1,2,3,4,5,7,8,34}
  # set  -> {1,2,3,4,5,7,8)
  ecs_services = [

    # each.value.name
    # each.value.image
    { name                = "flask"
      cpu                 = 512
      memory              = 1024
      container_port      = 5000
      # repo                = aws_ecr_repository.ecr["flask"].repository_url
      image               = "${aws_ecr_repository.ecr["flask"].repository_url}:latest"
      container_name      = "flask"
      container_port_name = "flask"
      

      vars = {
        DB_ADDRESS        = ""
        DB_NAME           = ""
        POSTGRES_USERNAME = ""
        POSTGRES_PASSWORD = ""

      }

    },
    { name                = "redis"
      cpu                 = 512
      memory              = 1024
      container_port      = 5000
      # repo                = aws_ecr_repository.ecr["redis"].repository_url
      image               = "${aws_ecr_repository.ecr["redis"].repository_url}:latest"
      container_name      = "redis"
      container_port_name = "redis"

      vars = {


      }

    },
    { name           = "nginx"
      cpu            = 512
      memory         = 1024
      container_port = 5000
      #   repo = aws_ecr_repository.ecr["nginx"].repository_url
      tag                 = "latest"
      # image               = "${aws_ecr_repository.ecr["nginx"].repository_url}:latest"
      container_name      = "nginx"
      container_port_name = "nginx"

      vars = {


      }

    },


  ]
  ecs_services_interpreted = { for svc in local.ecs_services : svc.name => svc }
  # ecs_services_interpreted = { for svc in local.ecs_services : svc.name => { for k, v in svc : k => v if k != "repo" } }
}

output "ecs_services" {
  value = local.ecs_services_interpreted
}