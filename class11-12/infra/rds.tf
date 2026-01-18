resource "aws_db_instance" "default" {
  allocated_storage      = 30
  identifier             = "student-portal-db"
  db_name                = "studentportal"
  engine                 = "postgres"
  engine_version         = "14.15"
  instance_class         = "db.t3.micro"
  username               = "postgres"
  password               = random_password.rds_password.result
  skip_final_snapshot    = true
  db_subnet_group_name   = aws_db_subnet_group.rds_subnet_group.name
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
}

# password 
# user aws_db_instance.default.username
# host aws_db_instance.default.address
# port aws_db_instance.default.port
# database_name aws_db_instance.default.db_name

# subnet group for rds -> list of subnets to use
resource "aws_db_subnet_group" "rds_subnet_group" {
  name       = "student-portaldb"
  subnet_ids = [aws_subnet.rds1.id, aws_subnet.rds2.id]

}


resource "random_password" "rds_password" {
  length           = 10
  special          = false
  override_special = "abcdefhjktyACJFSWRT123566"
}

# random_password.rds_password.result