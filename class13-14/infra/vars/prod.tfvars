environment = "prod"
DB_DEFAULT_SETTING = {
  DB_NAME                   = "appdb"
  USERNAME                  = "my_admin"
  DB_ENGINE                 = "postgres"
  DB_ENGINE_VERSION         = "14.15"
  DB_INSTANCE_CLASS         = "db.t3.micro"
  DB_ALLOCATED_STORAGE      = "50"
  DB_CLUSTER_INSTANCE_COUNT = "2"
  DB_CLUSTER_INSTANCE_CLASS = "db.t3.medium"
  DB_CLUSTER_ENGINE         = "aurora-postgresql"
  DB_CLUSTER_ENGINE_VERSION = "15.15"
}
