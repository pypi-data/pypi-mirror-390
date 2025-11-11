# AWS Infrastructure Example - SECURE VERSION
# This example shows the same infrastructure with security best practices applied
# Run: riveter scan -p aws-security -t secure.tf

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

# VPC with proper configuration and tags
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "main-vpc"
    Environment = "production"
    Owner       = "platform-team"
    Project     = "web-application"
    CostCenter  = "engineering"
  }
}

# Public subnet for load balancer only
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "us-west-2a"
  map_public_ip_on_launch = false  # ✅ Don't auto-assign public IPs

  tags = {
    Name        = "public-subnet-1"
    Environment = "production"
    Owner       = "platform-team"
    Project     = "web-application"
    CostCenter  = "engineering"
    Type        = "public"
  }
}

# Private subnet for application servers
resource "aws_subnet" "private" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "us-west-2a"

  tags = {
    Name        = "private-subnet-1"
    Environment = "production"
    Owner       = "platform-team"
    Project     = "web-application"
    CostCenter  = "engineering"
    Type        = "private"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name        = "main-igw"
    Environment = "production"
    Owner       = "platform-team"
    Project     = "web-application"
    CostCenter  = "engineering"
  }
}

# NAT Gateway for private subnet internet access
resource "aws_eip" "nat" {
  domain = "vpc"

  tags = {
    Name        = "nat-eip"
    Environment = "production"
    Owner       = "platform-team"
    Project     = "web-application"
    CostCenter  = "engineering"
  }
}

resource "aws_nat_gateway" "main" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public.id

  tags = {
    Name        = "main-nat-gateway"
    Environment = "production"
    Owner       = "platform-team"
    Project     = "web-application"
    CostCenter  = "engineering"
  }

  depends_on = [aws_internet_gateway.main]
}

# Route table for public subnet
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name        = "public-route-table"
    Environment = "production"
    Owner       = "platform-team"
    Project     = "web-application"
    CostCenter  = "engineering"
  }
}

# Route table for private subnet
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main.id
  }

  tags = {
    Name        = "private-route-table"
    Environment = "production"
    Owner       = "platform-team"
    Project     = "web-application"
    CostCenter  = "engineering"
  }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "private" {
  subnet_id      = aws_subnet.private.id
  route_table_id = aws_route_table.private.id
}

# SECURE: Restrictive security group for load balancer
resource "aws_security_group" "alb" {
  name_prefix = "alb-"
  vpc_id      = aws_vpc.main.id

  # ✅ Only HTTPS traffic allowed from internet
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # ✅ Restricted outbound to application servers only
  egress {
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = [aws_security_group.web.id]
  }

  tags = {
    Name        = "alb-security-group"
    Environment = "production"
    Owner       = "platform-team"
    Project     = "web-application"
    CostCenter  = "engineering"
  }
}

# SECURE: Security group for web servers (no direct internet access)
resource "aws_security_group" "web" {
  name_prefix = "web-"
  vpc_id      = aws_vpc.main.id

  # ✅ Only HTTP from load balancer
  ingress {
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  # ✅ SSH only from bastion host (if needed)
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]  # Only from VPC
  }

  # ✅ Restricted outbound for updates and database
  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # HTTPS for updates
  }

  egress {
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.database.id]
  }

  tags = {
    Name        = "web-security-group"
    Environment = "production"
    Owner       = "platform-team"
    Project     = "web-application"
    CostCenter  = "engineering"
  }
}

# SECURE: Database security group
resource "aws_security_group" "database" {
  name_prefix = "database-"
  vpc_id      = aws_vpc.main.id

  # ✅ Only MySQL from web servers
  ingress {
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.web.id]
  }

  # ✅ No outbound rules needed for database

  tags = {
    Name        = "database-security-group"
    Environment = "production"
    Owner       = "platform-team"
    Project     = "web-application"
    CostCenter  = "engineering"
  }
}

# SECURE: EC2 instance in private subnet with encryption
resource "aws_instance" "web" {
  ami                    = "ami-0c02fb55956c7d316"  # Amazon Linux 2
  instance_type          = "t3.micro"
  subnet_id              = aws_subnet.private.id  # ✅ Private subnet
  vpc_security_group_ids = [aws_security_group.web.id]

  # ✅ No public IP assigned
  associate_public_ip_address = false

  # ✅ Encrypted root volume
  root_block_device {
    volume_size = 20
    volume_type = "gp3"
    encrypted   = true
  }

  # ✅ Monitoring enabled
  monitoring = true

  # ✅ IMDSv2 enforced
  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"
  }

  tags = {
    Name        = "web-server"
    Environment = "production"
    Owner       = "platform-team"
    Project     = "web-application"
    CostCenter  = "engineering"
    Backup      = "daily"
  }
}

# SECURE: S3 bucket with proper security
resource "aws_s3_bucket" "data" {
  bucket        = "secure-data-bucket-${random_id.suffix.hex}"
  force_destroy = true

  tags = {
    Name        = "application-data"
    Environment = "production"
    Owner       = "platform-team"
    Project     = "web-application"
    CostCenter  = "engineering"
  }
}

# ✅ Versioning enabled
resource "aws_s3_bucket_versioning" "data" {
  bucket = aws_s3_bucket.data.id
  versioning_configuration {
    status = "Enabled"
  }
}

# ✅ Encryption enabled
resource "aws_s3_bucket_server_side_encryption_configuration" "data" {
  bucket = aws_s3_bucket.data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# ✅ Public access blocked
resource "aws_s3_bucket_public_access_block" "data" {
  bucket = aws_s3_bucket.data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# SECURE: RDS instance with proper security
resource "aws_db_subnet_group" "main" {
  name       = "main-db-subnet-group"
  subnet_ids = [aws_subnet.private.id, aws_subnet.public.id]  # Need 2+ subnets

  tags = {
    Name        = "main-db-subnet-group"
    Environment = "production"
    Owner       = "platform-team"
    Project     = "web-application"
    CostCenter  = "engineering"
  }
}

# Create a second private subnet for RDS (required for subnet group)
resource "aws_subnet" "private_2" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.3.0/24"
  availability_zone = "us-west-2b"

  tags = {
    Name        = "private-subnet-2"
    Environment = "production"
    Owner       = "platform-team"
    Project     = "web-application"
    CostCenter  = "engineering"
    Type        = "private"
  }
}

# Update subnet group to use both private subnets
resource "aws_db_subnet_group" "main_updated" {
  name       = "main-db-subnet-group-updated"
  subnet_ids = [aws_subnet.private.id, aws_subnet.private_2.id]

  tags = {
    Name        = "main-db-subnet-group"
    Environment = "production"
    Owner       = "platform-team"
    Project     = "web-application"
    CostCenter  = "engineering"
  }
}

resource "aws_db_instance" "main" {
  identifier     = "main-database"
  engine         = "mysql"
  engine_version = "8.0"
  instance_class = "db.t3.micro"

  allocated_storage = 20
  storage_type      = "gp3"  # ✅ Latest storage type
  storage_encrypted = true   # ✅ Encryption enabled

  db_name  = "myapp"
  username = "admin"
  manage_master_user_password = true  # ✅ AWS manages password

  db_subnet_group_name = aws_db_subnet_group.main_updated.name
  publicly_accessible  = false  # ✅ Not publicly accessible
  multi_az             = true   # ✅ High availability

  backup_retention_period = 7     # ✅ 7 days backup retention
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  skip_final_snapshot = false
  final_snapshot_identifier = "main-database-final-snapshot"

  vpc_security_group_ids = [aws_security_group.database.id]

  # ✅ Enhanced monitoring
  monitoring_interval = 60
  monitoring_role_arn = aws_iam_role.rds_monitoring.arn

  tags = {
    Name        = "main-database"
    Environment = "production"
    Owner       = "platform-team"
    Project     = "web-application"
    CostCenter  = "engineering"
    Backup      = "automated"
  }
}

# IAM role for RDS enhanced monitoring
resource "aws_iam_role" "rds_monitoring" {
  name = "rds-monitoring-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "rds-monitoring-role"
    Environment = "production"
    Owner       = "platform-team"
    Project     = "web-application"
    CostCenter  = "engineering"
  }
}

resource "aws_iam_role_policy_attachment" "rds_monitoring" {
  role       = aws_iam_role.rds_monitoring.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

resource "random_id" "suffix" {
  byte_length = 4
}

# Secure outputs (no sensitive information exposed)
output "vpc_id" {
  value       = aws_vpc.main.id
  description = "VPC ID for reference"
}

output "private_subnet_id" {
  value       = aws_subnet.private.id
  description = "Private subnet ID where application runs"
}