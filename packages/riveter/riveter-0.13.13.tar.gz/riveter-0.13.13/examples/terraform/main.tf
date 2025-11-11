provider "aws" {
  region = "us-west-2"
}

# --------------------
# VPC and Subnet Setup
# --------------------
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  enable_dns_hostnames = false
}

resource "aws_subnet" "main" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-west-2a"

  tags = {
    Name        = "main-subnet"
    Environment = "production"
    Owner       = "platform-team"
    Project     = "e-commerce"
    CostCenter  = "12345"
  }
}

# --------------------
# EC2 + EBS Setup
# --------------------
resource "aws_security_group" "web_sg" {
  name        = "web-server-sg"
  description = "Allow SSH"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "web" {
  ami                         = "ami-0c55b159cbfafe1f0"
  instance_type               = "t3.micro"
  subnet_id                   = aws_subnet.main.id
  vpc_security_group_ids      = [aws_security_group.web_sg.id]
  associate_public_ip_address = true
  key_name                    = "my-keypair" # Replace with your actual key pair

  root_block_device {
    volume_size = 100
    volume_type = "gp3"
    encrypted   = false
  }

  tags = {
    Name        = "web-server-prod-1"
    Environment = "production"
    Owner       = "platform-team"
    CostCenter  = "12345"
    Project     = "e-commerce"
    Backup      = "daily"
  }
}

resource "aws_ebs_volume" "web_data" {
  availability_zone = "us-west-2a"
  size              = 100
  type              = "gp3"
  encrypted         = true

  tags = {
    Name = "web-server-data-volume"
  }
}

resource "aws_volume_attachment" "web_data_attach" {
  device_name = "/dev/sdf"
  volume_id   = aws_ebs_volume.web_data.id
  instance_id = aws_instance.web.id
  force_detach = true
}

# --------------------
# RDS Instance Setup
# --------------------
resource "aws_db_subnet_group" "rds_subnet_group" {
  name       = "rds-subnet-group"
  subnet_ids = [aws_subnet.main.id]

  tags = {
    Name = "RDS subnet group"
  }
}

resource "aws_db_instance" "postgres" {
  identifier              = "rds-prod-main"
  instance_class          = "db.r6g.2xlarge"
  engine                  = "postgres"
  engine_version          = "15.3"
  allocated_storage       = 500
  storage_type            = "gp3"
  storage_encrypted        = true
  username                = "adminuser"
  password                = "AdminPass123!" # WARNING: use secrets manager or variables for real deployments
  db_subnet_group_name    = aws_db_subnet_group.rds_subnet_group.name
  multi_az                = true
  publicly_accessible     = true
  backup_retention_period = 30
  maintenance_window      = "mon:04:00-mon:05:00"
  skip_final_snapshot     = true

  vpc_security_group_ids = [aws_security_group.web_sg.id]

  tags = {
    Name        = "production-database"
    Environment = "production"
    Owner       = "dba-team"
    CostCenter  = "12345"
    Project     = "e-commerce"
    Backup      = "hourly"
  }
}

# --------------------
# S3 Bucket Setup
# --------------------
resource "aws_s3_bucket" "static_assets" {
  bucket = "prod-static-assets-${random_id.suffix.hex}"
  force_destroy = true

  tags = {
    Name        = "production-static-assets"
    Environment = "production"
    Project     = "e-commerce"
  }
}

resource "aws_s3_bucket_versioning" "static_assets_versioning" {
  bucket = aws_s3_bucket.static_assets.id

  versioning_configuration {
    status = "Disabled"
  }
}

resource "aws_s3_bucket_logging" "static_assets_logging" {
  bucket = aws_s3_bucket.static_assets.id

  target_bucket = aws_s3_bucket.static_assets.id
  target_prefix = "logs/"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "static_assets_encryption" {
  bucket = aws_s3_bucket.static_assets.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "static_assets_lifecycle" {
  bucket = aws_s3_bucket.static_assets.id

  rule {
    id     = "archive-old-files"
    status = "Enabled"

    transition {
      days          = 90
      storage_class = "GLACIER"
    }
  }
}

resource "aws_s3_bucket_cors_configuration" "static_assets_cors" {
  bucket = aws_s3_bucket.static_assets.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET"]
    allowed_origins = ["https://www.example.com"]
    max_age_seconds = 3600
  }
}

resource "aws_s3_bucket_public_access_block" "static_assets_public_access" {
  bucket = aws_s3_bucket.static_assets.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "random_id" "suffix" {
  byte_length = 4
}
