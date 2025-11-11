# AWS Well-Architected Framework Test Fixtures
# This file contains both passing and failing examples for aws-well-architected rule pack

# ============================================================================
# OPERATIONAL EXCELLENCE PILLAR
# ============================================================================

# PASS: EC2 instance with CloudWatch alarms
resource "aws_instance" "monitored_instance" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"

  monitoring = true

  tags = {
    Name        = "monitored-instance"
    Environment = "production"
    CostCenter  = "engineering"
    Project     = "web-app"
  }
}

resource "aws_cloudwatch_metric_alarm" "cpu_alarm" {
  alarm_name          = "high-cpu-utilization"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "This metric monitors ec2 cpu utilization"
  alarm_actions       = ["arn:aws:sns:us-east-1:123456789012:alerts"]

  dimensions = {
    InstanceId = aws_instance.monitored_instance.id
  }
}

# FAIL: EC2 instance without CloudWatch alarms
resource "aws_instance" "unmonitored_instance" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"

  monitoring = false

  tags = {
    Name        = "unmonitored-instance"
    Environment = "production"
  }
}

# PASS: Auto Scaling group with proper configuration
resource "aws_autoscaling_group" "web_asg" {
  name                = "web-asg"
  vpc_zone_identifier = ["subnet-12345", "subnet-67890"]
  min_size            = 2
  max_size            = 6
  desired_capacity    = 3
  health_check_type   = "ELB"
  health_check_grace_period = 300

  launch_template {
    id      = aws_launch_template.web_lt.id
    version = "$Latest"
  }

  tag {
    key                 = "Name"
    value               = "web-server"
    propagate_at_launch = true
  }

  tag {
    key                 = "Environment"
    value               = "production"
    propagate_at_launch = true
  }
}

resource "aws_autoscaling_policy" "scale_up" {
  name                   = "scale-up"
  scaling_adjustment     = 1
  adjustment_type        = "ChangeInCapacity"
  cooldown               = 300
  autoscaling_group_name = aws_autoscaling_group.web_asg.name
}

# FAIL: Resources without proper tagging for operations
resource "aws_instance" "untagged_instance" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"
}

# ============================================================================
# SECURITY PILLAR
# ============================================================================

# PASS: S3 bucket with versioning and encryption
resource "aws_s3_bucket" "secure_bucket" {
  bucket = "secure-bucket-12345"

  tags = {
    Environment = "production"
    Compliance  = "required"
  }
}

resource "aws_s3_bucket_versioning" "secure_bucket_versioning" {
  bucket = aws_s3_bucket.secure_bucket.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "secure_bucket_encryption" {
  bucket = aws_s3_bucket.secure_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.s3_key.arn
    }
  }
}

resource "aws_s3_bucket_public_access_block" "secure_bucket_pab" {
  bucket = aws_s3_bucket.secure_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# PASS: VPC with flow logs
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "main-vpc"
    Environment = "production"
  }
}

resource "aws_flow_log" "vpc_flow_log" {
  iam_role_arn    = aws_iam_role.flow_log_role.arn
  log_destination = aws_cloudwatch_log_group.flow_log_group.arn
  traffic_type    = "ALL"
  vpc_id          = aws_vpc.main.id
}

# FAIL: VPC without flow logs
resource "aws_vpc" "no_flow_logs" {
  cidr_block = "10.1.0.0/16"

  tags = {
    Name        = "no-flow-logs-vpc"
    Environment = "production"
  }
}

# ============================================================================
# RELIABILITY PILLAR
# ============================================================================

# PASS: RDS with Multi-AZ deployment
resource "aws_db_instance" "multi_az_db" {
  identifier           = "multi-az-database"
  engine               = "postgres"
  engine_version       = "14.7"
  instance_class       = "db.t3.micro"
  allocated_storage    = 20
  storage_encrypted    = true
  multi_az             = true
  publicly_accessible  = false
  skip_final_snapshot  = true

  backup_retention_period = 7
  backup_window           = "03:00-04:00"
  maintenance_window      = "mon:04:00-mon:05:00"

  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]

  tags = {
    Name        = "multi-az-database"
    Environment = "production"
  }
}

# FAIL: RDS without Multi-AZ in production
resource "aws_db_instance" "single_az_db" {
  identifier          = "single-az-database"
  engine              = "postgres"
  engine_version      = "14.7"
  instance_class      = "db.t3.micro"
  allocated_storage   = 20
  multi_az            = false
  skip_final_snapshot = true

  tags = {
    Name        = "single-az-database"
    Environment = "production"
  }
}

# PASS: ELB with health checks
resource "aws_lb" "app_lb" {
  name               = "app-load-balancer"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.lb_sg.id]
  subnets            = ["subnet-12345", "subnet-67890"]

  enable_deletion_protection = true
  enable_http2               = true

  tags = {
    Name        = "app-lb"
    Environment = "production"
  }
}

resource "aws_lb_target_group" "app_tg" {
  name     = "app-target-group"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id

  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    path                = "/health"
    matcher             = "200"
  }

  tags = {
    Name        = "app-tg"
    Environment = "production"
  }
}

# FAIL: ELB without proper health checks
resource "aws_lb_target_group" "no_health_check" {
  name     = "no-health-check-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id

  health_check {
    enabled = false
  }
}

# PASS: DynamoDB with point-in-time recovery
resource "aws_dynamodb_table" "app_table" {
  name           = "app-table"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"

  attribute {
    name = "id"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }

  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.dynamodb_key.arn
  }

  tags = {
    Name        = "app-table"
    Environment = "production"
  }
}

# FAIL: DynamoDB without point-in-time recovery
resource "aws_dynamodb_table" "no_pitr" {
  name         = "no-pitr-table"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }

  point_in_time_recovery {
    enabled = false
  }
}

# PASS: EBS volume with snapshot
resource "aws_ebs_volume" "data_volume" {
  availability_zone = "us-east-1a"
  size              = 100
  type              = "gp3"
  encrypted         = true
  kms_key_id        = aws_kms_key.ebs_key.arn

  tags = {
    Name        = "data-volume"
    Environment = "production"
    Backup      = "daily"
  }
}

resource "aws_ebs_snapshot" "data_snapshot" {
  volume_id = aws_ebs_volume.data_volume.id

  tags = {
    Name = "data-snapshot"
  }
}

# ============================================================================
# PERFORMANCE EFFICIENCY PILLAR
# ============================================================================

# PASS: CloudFront distribution
resource "aws_cloudfront_distribution" "cdn" {
  enabled             = true
  is_ipv6_enabled     = true
  comment             = "CDN for static assets"
  default_root_object = "index.html"

  origin {
    domain_name = aws_s3_bucket.secure_bucket.bucket_regional_domain_name
    origin_id   = "S3-secure-bucket"

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.oai.cloudfront_access_identity_path
    }
  }

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-secure-bucket"

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
    compress               = true
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  tags = {
    Name        = "cdn"
    Environment = "production"
  }
}

# PASS: ElastiCache cluster
resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "app-cache"
  engine               = "redis"
  node_type            = "cache.t3.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  engine_version       = "7.0"
  port                 = 6379
  subnet_group_name    = aws_elasticache_subnet_group.cache_subnet.name
  security_group_ids   = [aws_security_group.cache_sg.id]

  at_rest_encryption_enabled = true
  transit_encryption_enabled = true

  tags = {
    Name        = "app-cache"
    Environment = "production"
  }
}

# PASS: EBS volume with optimal type
resource "aws_ebs_volume" "high_performance" {
  availability_zone = "us-east-1a"
  size              = 100
  type              = "gp3"
  iops              = 3000
  throughput        = 125
  encrypted         = true

  tags = {
    Name        = "high-performance-volume"
    Environment = "production"
  }
}

# FAIL: EBS volume with suboptimal type
resource "aws_ebs_volume" "low_performance" {
  availability_zone = "us-east-1a"
  size              = 100
  type              = "gp2"
  encrypted         = true

  tags = {
    Name        = "low-performance-volume"
    Environment = "production"
  }
}

# PASS: Lambda with appropriate memory
resource "aws_lambda_function" "optimized_lambda" {
  filename      = "lambda.zip"
  function_name = "optimized-function"
  role          = aws_iam_role.lambda_role.arn
  handler       = "index.handler"
  runtime       = "python3.11"
  memory_size   = 1024
  timeout       = 30

  environment {
    variables = {
      ENVIRONMENT = "production"
    }
  }

  tags = {
    Name        = "optimized-function"
    Environment = "production"
  }
}

# FAIL: Lambda with default memory
resource "aws_lambda_function" "default_lambda" {
  filename      = "lambda.zip"
  function_name = "default-function"
  role          = aws_iam_role.lambda_role.arn
  handler       = "index.handler"
  runtime       = "python3.11"
  memory_size   = 128

  tags = {
    Name        = "default-function"
    Environment = "production"
  }
}

# ============================================================================
# COST OPTIMIZATION PILLAR
# ============================================================================

# PASS: Resources with cost allocation tags
resource "aws_instance" "cost_tagged" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"

  tags = {
    Name        = "cost-tagged-instance"
    Environment = "production"
    CostCenter  = "engineering"
    Project     = "web-app"
    Owner       = "platform-team"
  }
}

# FAIL: Resources without cost allocation tags
resource "aws_instance" "no_cost_tags" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"

  tags = {
    Name = "no-cost-tags-instance"
  }
}

# PASS: S3 bucket with lifecycle policy
resource "aws_s3_bucket" "lifecycle_bucket" {
  bucket = "lifecycle-bucket-12345"

  tags = {
    Environment = "production"
    CostCenter  = "engineering"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "lifecycle_config" {
  bucket = aws_s3_bucket.lifecycle_bucket.id

  rule {
    id     = "transition-to-ia"
    status = "Enabled"

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    expiration {
      days = 365
    }
  }
}

# FAIL: S3 bucket without lifecycle policy
resource "aws_s3_bucket" "no_lifecycle" {
  bucket = "no-lifecycle-bucket-12345"

  tags = {
    Environment = "production"
  }
}

# PASS: EBS volume with appropriate size
resource "aws_ebs_volume" "right_sized" {
  availability_zone = "us-east-1a"
  size              = 20
  type              = "gp3"
  encrypted         = true

  tags = {
    Name        = "right-sized-volume"
    Environment = "production"
    CostCenter  = "engineering"
  }
}

# FAIL: Oversized EBS volume
resource "aws_ebs_volume" "oversized" {
  availability_zone = "us-east-1a"
  size              = 1000
  type              = "gp3"
  encrypted         = true

  tags = {
    Name        = "oversized-volume"
    Environment = "development"
  }
}

# ============================================================================
# SUSTAINABILITY PILLAR
# ============================================================================

# PASS: Lambda function (serverless)
resource "aws_lambda_function" "sustainable_lambda" {
  filename      = "lambda.zip"
  function_name = "sustainable-function"
  role          = aws_iam_role.lambda_role.arn
  handler       = "index.handler"
  runtime       = "python3.11"

  tags = {
    Name        = "sustainable-function"
    Environment = "production"
    Architecture = "serverless"
  }
}

# PASS: Fargate task (serverless containers)
resource "aws_ecs_task_definition" "fargate_task" {
  family                   = "fargate-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"

  container_definitions = jsonencode([
    {
      name  = "app"
      image = "nginx:latest"
      portMappings = [
        {
          containerPort = 80
          protocol      = "tcp"
        }
      ]
    }
  ])

  tags = {
    Name         = "fargate-task"
    Environment  = "production"
    Architecture = "serverless"
  }
}

# PASS: Instance with appropriate size for workload
resource "aws_instance" "right_sized_instance" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"

  tags = {
    Name        = "right-sized-instance"
    Environment = "production"
    Workload    = "low-traffic-web"
  }
}

# FAIL: Oversized instance for workload
resource "aws_instance" "oversized_instance" {
  ami           = "ami-12345678"
  instance_type = "m5.24xlarge"

  tags = {
    Name        = "oversized-instance"
    Environment = "development"
    Workload    = "testing"
  }
}

# ============================================================================
# SUPPORTING RESOURCES
# ============================================================================

resource "aws_launch_template" "web_lt" {
  name_prefix   = "web-"
  image_id      = "ami-12345678"
  instance_type = "t3.micro"

  monitoring {
    enabled = true
  }

  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 1
  }
}

resource "aws_security_group" "lb_sg" {
  name        = "lb-security-group"
  description = "Security group for load balancer"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 443
    to_port     = 443
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

resource "aws_security_group" "cache_sg" {
  name        = "cache-security-group"
  description = "Security group for ElastiCache"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }
}

resource "aws_elasticache_subnet_group" "cache_subnet" {
  name       = "cache-subnet-group"
  subnet_ids = ["subnet-12345", "subnet-67890"]
}

resource "aws_cloudwatch_log_group" "flow_log_group" {
  name              = "/aws/vpc/flow-logs"
  retention_in_days = 30
}

resource "aws_iam_role" "flow_log_role" {
  name = "flow-log-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "vpc-flow-logs.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role" "lambda_role" {
  name = "lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_kms_key" "s3_key" {
  description             = "KMS key for S3"
  deletion_window_in_days = 30
  enable_key_rotation     = true
}

resource "aws_kms_key" "ebs_key" {
  description             = "KMS key for EBS"
  deletion_window_in_days = 30
  enable_key_rotation     = true
}

resource "aws_kms_key" "dynamodb_key" {
  description             = "KMS key for DynamoDB"
  deletion_window_in_days = 30
  enable_key_rotation     = true
}

resource "aws_cloudfront_origin_access_identity" "oai" {
  comment = "OAI for S3 bucket"
}
