# rds password -> random [provider
resource "random_password" "rds_password" {
  length           = 10
  special          = false
  override_special = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
}

# secret manager
resource "aws_secretsmanager_secret" "db_password" {
  name                    = "${var.environment}-${var.app_name}-db"
  recovery_window_in_days = 7
}

resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id     = aws_secretsmanager_secret.db_password.id
  secret_string = random_password.rds_password.result
}

# secret version


# DB subnet group
resource "aws_db_subnet_group" "rds_subnet_group" {
  name = "${var.environment}-${var.app_name}-db-subnetgroup"
  # subnet_ids = [aws_subnet.rds[0].id, aws_subnet.rds[1].id]
  subnet_ids = aws_subnet.rds[*].id
}


# (1,2,3,4) -> Tuple like a list but immutable
# [1,2,3,4] -> list -> mutable
# kms key
resource "aws_kms_key" "rds_kms" {
  description             = "KMS key for RDS encryption"
  deletion_window_in_days = 10
}
resource "aws_kms_alias" "rds_kms" {
  name          = "alias/${var.environment}-${var.app_name}-db"
  target_key_id = aws_kms_key.rds_kms.key_id
}
# for dev -> create an rds instance in dev vpc

resource "aws_db_instance" "default" {
  # if else conditional 
  count                  = var.environment == "dev" ? 1 : 0
  identifier             = "${var.environment}-${var.app_name}-db"
  allocated_storage      = var.DB_DEFAULT_SETTING.DB_ALLOCATED_STORAGE
  db_name                = var.DB_DEFAULT_SETTING.DB_NAME
  engine                 = var.DB_DEFAULT_SETTING.DB_ENGINE
  engine_version         = var.DB_DEFAULT_SETTING.DB_ENGINE_VERSION
  instance_class         = var.DB_DEFAULT_SETTING.DB_INSTANCE_CLASS
  username               = var.DB_DEFAULT_SETTING.USERNAME
  password               = random_password.rds_password.result
  skip_final_snapshot    = true
  db_subnet_group_name   = aws_db_subnet_group.rds_subnet_group.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  kms_key_id             = aws_kms_key.rds_kms.arn
  storage_encrypted      = true
}


# for prod -> create an rds cluster (1 writer, 1 reader) in prod vpc

resource "aws_rds_cluster" "aurora_cluster" {
  count                  = var.environment == "prod" ? 1 : 0
  cluster_identifier     = "${var.environment}-${var.app_name}-cluster"
  engine                 = var.DB_DEFAULT_SETTING.DB_CLUSTER_ENGINE
  engine_version         = var.DB_DEFAULT_SETTING.DB_CLUSTER_ENGINE_VERSION
  database_name          = var.DB_DEFAULT_SETTING.DB_NAME
  master_username        = var.DB_DEFAULT_SETTING.USERNAME
  master_password        = random_password.rds_password.result
  db_subnet_group_name   = aws_db_subnet_group.rds_subnet_group.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  kms_key_id             = aws_kms_key.rds_kms.arn
  storage_encrypted      = true
  skip_final_snapshot    = true
}

# Writer instance
resource "aws_rds_cluster_instance" "writer" {
  count              = var.environment == "prod" ? 1 : 0
  identifier         = "${var.environment}-${var.app_name}-writer"
  cluster_identifier = aws_rds_cluster.aurora_cluster[0].id
  instance_class     = var.DB_DEFAULT_SETTING.DB_CLUSTER_INSTANCE_CLASS
  engine             = aws_rds_cluster.aurora_cluster[0].engine
  engine_version     = aws_rds_cluster.aurora_cluster[0].engine_version
}

# Reader instance
resource "aws_rds_cluster_instance" "reader" {
  count              = var.environment == "prod" ? 1 : 0
  identifier         = "${var.environment}-${var.app_name}-reader"
  cluster_identifier = aws_rds_cluster.aurora_cluster[0].id
  instance_class     = var.DB_DEFAULT_SETTING.DB_CLUSTER_INSTANCE_CLASS
  engine             = aws_rds_cluster.aurora_cluster[0].engine
  engine_version     = aws_rds_cluster.aurora_cluster[0].engine_version
}




