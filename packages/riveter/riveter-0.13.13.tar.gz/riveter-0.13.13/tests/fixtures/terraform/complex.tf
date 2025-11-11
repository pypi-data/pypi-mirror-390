resource "aws_instance" "web_server_1" {
  ami           = "ami-12345678"
  instance_type = "t3.small"

  tags = {
    Name        = "web-server-1"
    Environment = "production"
    CostCenter  = "12345"
    Team        = "backend"
  }

  root_block_device {
    volume_size = 50
    volume_type = "gp3"
    encrypted   = true
  }

  security_groups = ["sg-12345678", "sg-87654321"]
}

resource "aws_instance" "web_server_2" {
  ami           = "ami-87654321"
  instance_type = "t3.medium"

  tags = {
    Name        = "web-server-2"
    Environment = "staging"
    Team        = "frontend"
  }

  root_block_device {
    volume_size = 30
    volume_type = "gp2"
  }

  security_groups = ["sg-12345678"]
}

resource "aws_s3_bucket" "data_bucket" {
  bucket = "company-data-bucket"

  tags = {
    Environment = "production"
    Purpose     = "data-storage"
    Compliance  = "SOX"
  }
}

resource "aws_s3_bucket" "logs_bucket" {
  bucket = "company-logs-bucket"

  tags = {
    Environment = "production"
    Team        = "devops"
  }
}

resource "aws_rds_instance" "primary_db" {
  engine         = "postgresql"
  engine_version = "14.9"
  instance_class = "db.t3.small"
  allocated_storage = 100

  tags = {
    Environment = "production"
    Name        = "primary-database"
    CostCenter  = "12345"
    Backup      = "daily"
  }
}

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"

  tags = {
    Name        = "main-vpc"
    Environment = "production"
  }
}
