# AWS Infrastructure Example - INSECURE VERSION
# This example contains intentional security violations for learning purposes
# Run: riveter scan -p aws-security -t insecure.tf

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-west-2"
}

# VPC with minimal configuration
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  # Missing required tags - will fail validation
}

# Public subnet
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "us-west-2a"
  map_public_ip_on_launch = true

  # Missing required tags - will fail validation
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  # Missing required tags - will fail validation
}

# Route table for public subnet
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  # Missing required tags - will fail validation
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# INSECURE: Overly permissive security group
resource "aws_security_group" "web" {
  name_prefix = "web-"
  vpc_id      = aws_vpc.main.id

  # PROBLEM: SSH open to the world
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # ❌ Should be restricted
  }

  # PROBLEM: HTTP open to the world (should use HTTPS)
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # ❌ Should use HTTPS only
  }

  # PROBLEM: All outbound traffic allowed
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]  # ❌ Should be restricted
  }

  # Missing required tags - will fail validation
}

# INSECURE: EC2 instance with public IP and unencrypted storage
resource "aws_instance" "web" {
  ami                         = "ami-0c02fb55956c7d316"  # Amazon Linux 2
  instance_type               = "t3.micro"
  subnet_id                   = aws_subnet.public.id
  vpc_security_group_ids      = [aws_security_group.web.id]
  associate_public_ip_address = true  # ❌ Should not have public IP in production

  # PROBLEM: Unencrypted root volume
  root_block_device {
    volume_size = 20
    volume_type = "gp3"
    encrypted   = false  # ❌ Should be encrypted
  }

  # PROBLEM: No monitoring enabled
  monitoring = false  # ❌ Should enable detailed monitoring

  # Missing required tags - will fail validation
}

# INSECURE: S3 bucket with public access
resource "aws_s3_bucket" "data" {
  bucket        = "my-insecure-data-bucket-${random_id.suffix.hex}"
  force_destroy = true

  # Missing required tags - will fail validation
}

# PROBLEM: No versioning enabled
resource "aws_s3_bucket_versioning" "data" {
  bucket = aws_s3_bucket.data.id
  versioning_configuration {
    status = "Disabled"  # ❌ Should be enabled
  }
}

# PROBLEM: No encryption configured
# Missing aws_s3_bucket_server_side_encryption_configuration

# PROBLEM: Public access not blocked
resource "aws_s3_bucket_public_access_block" "data" {
  bucket = aws_s3_bucket.data.id

  block_public_acls       = false  # ❌ Should be true
  block_public_policy     = false  # ❌ Should be true
  ignore_public_acls      = false  # ❌ Should be true
  restrict_public_buckets = false  # ❌ Should be true
}

# INSECURE: RDS instance with public access and weak configuration
resource "aws_db_subnet_group" "main" {
  name       = "main-db-subnet-group"
  subnet_ids = [aws_subnet.public.id]

  # Missing required tags - will fail validation
}

resource "aws_db_instance" "main" {
  identifier     = "main-database"
  engine         = "mysql"
  engine_version = "8.0"
  instance_class = "db.t3.micro"

  allocated_storage = 20
  storage_type      = "gp2"  # ❌ Should use gp3
  storage_encrypted = false  # ❌ Should be encrypted

  db_name  = "myapp"
  username = "admin"
  password = "password123"  # ❌ Should use secrets manager

  db_subnet_group_name = aws_db_subnet_group.main.name
  publicly_accessible  = true   # ❌ Should be false
  multi_az            = false   # ❌ Should be true for production

  backup_retention_period = 0   # ❌ Should be at least 7 days
  skip_final_snapshot    = true

  vpc_security_group_ids = [aws_security_group.web.id]

  # Missing required tags - will fail validation
}

resource "random_id" "suffix" {
  byte_length = 4
}

# Output the public IP (which we shouldn't have!)
output "web_public_ip" {
  value = aws_instance.web.public_ip
  description = "Public IP of web server (INSECURE - should not exist!)"
}

output "database_endpoint" {
  value = aws_db_instance.main.endpoint
  description = "Database endpoint (INSECURE - publicly accessible!)"
}