# AWS HIPAA Compliance Test Fixtures
# This file contains both passing and failing resources for HIPAA compliance testing

# ============================================================================
# ENCRYPTION RULES - Passing Examples
# ============================================================================

# PASS: S3 bucket with PHI tag and encryption
resource "aws_s3_bucket" "phi_encrypted" {
  bucket = "healthcare-phi-data-encrypted"

  tags = {
    DataClassification = "PHI"
    Environment        = "production"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "phi_encrypted" {
  bucket = aws_s3_bucket.phi_encrypted.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# PASS: RDS with PHI tag and encryption
resource "aws_db_instance" "phi_database" {
  identifier          = "healthcare-phi-db"
  engine              = "postgres"
  instance_class      = "db.t3.medium"
  allocated_storage   = 100
  storage_encrypted   = true
  publicly_accessible = false
  backup_retention_period = 14

  enabled_cloudwatch_logs_exports = ["postgresql"]

  tags = {
    DataClassification = "PHI"
    Environment        = "production"
  }
}

# PASS: EBS volume with encryption
resource "aws_ebs_volume" "encrypted_volume" {
  availability_zone = "us-east-1a"
  size              = 100
  encrypted         = true
  type              = "gp3"

  tags = {
    Name = "encrypted-ebs-volume"
  }
}

# PASS: EC2 instance with encrypted root volume
resource "aws_instance" "encrypted_instance" {
  ami           = "ami-12345678"
  instance_type = "t3.medium"

  root_block_device {
    encrypted = true
  }

  tags = {
    Name = "encrypted-instance"
  }
}

# PASS: KMS key with rotation enabled
resource "aws_kms_key" "hipaa_key" {
  description             = "KMS key for HIPAA-compliant encryption"
  enable_key_rotation     = true
  deletion_window_in_days = 30

  tags = {
    Purpose = "HIPAA-Encryption"
  }
}

# PASS: CloudFront with TLS 1.2
resource "aws_cloudfront_distribution" "secure_distribution" {
  enabled = true

  origin {
    domain_name = "example.com"
    origin_id   = "example"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "example"
    viewer_protocol_policy = "redirect-to-https"

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = false
    minimum_protocol_version       = "TLSv1.2_2021"
    ssl_support_method             = "sni-only"
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
}

# PASS: ALB with HTTPS listener
resource "aws_lb_listener" "https_listener" {
  load_balancer_arn = aws_lb.application.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn   = "arn:aws:acm:us-east-1:123456789012:certificate/12345678"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.main.arn
  }
}

resource "aws_lb" "application" {
  name               = "hipaa-alb"
  internal           = false
  load_balancer_type = "application"
  subnets            = ["subnet-12345", "subnet-67890"]

  access_logs {
    enabled = true
    bucket  = "alb-logs-bucket"
  }

  tags = {
    Environment = "production"
  }
}

resource "aws_lb_target_group" "main" {
  name     = "main-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = "vpc-12345"
}

# PASS: ElastiCache with encryption
resource "aws_elasticache_replication_group" "encrypted_cache" {
  replication_group_id       = "hipaa-cache"
  replication_group_description = "HIPAA-compliant cache"
  engine                     = "redis"
  node_type                  = "cache.t3.medium"
  number_cache_clusters      = 2
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true

  tags = {
    Environment = "production"
  }
}

# PASS: Redshift with encryption
resource "aws_redshift_cluster" "encrypted_warehouse" {
  cluster_identifier  = "hipaa-warehouse"
  database_name       = "healthcare"
  master_username     = "admin"
  master_password     = "SecurePassword123!"
  node_type           = "dc2.large"
  cluster_type        = "single-node"
  encrypted           = true
  publicly_accessible = false

  logging {
    enable = true
  }

  tags = {
    Environment = "production"
  }
}

# ============================================================================
# ACCESS CONTROL RULES - Passing Examples
# ============================================================================

# PASS: IAM user without force_destroy
resource "aws_iam_user" "hipaa_user" {
  name          = "hipaa-user"
  force_destroy = false

  tags = {
    Department = "Healthcare"
  }
}

# PASS: IAM policy without wildcard actions
resource "aws_iam_policy" "least_privilege" {
  name        = "least-privilege-policy"
  description = "Policy following least privilege principle"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Resource = "arn:aws:s3:::specific-bucket/*"
      }
    ]
  })
}

# PASS: S3 bucket with public access blocked
resource "aws_s3_bucket_public_access_block" "phi_bucket_block" {
  bucket = aws_s3_bucket.phi_encrypted.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# PASS: EC2 instance with PHI tag and no public IP
resource "aws_instance" "phi_instance" {
  ami                         = "ami-12345678"
  instance_type               = "t3.medium"
  associate_public_ip_address = false

  root_block_device {
    encrypted = true
  }

  tags = {
    DataClassification = "PHI"
    Environment        = "production"
  }
}

# PASS: IAM password policy with strong requirements
resource "aws_iam_account_password_policy" "strict" {
  minimum_password_length        = 14
  require_uppercase_characters   = true
  require_lowercase_characters   = true
  require_numbers                = true
  require_symbols                = true
  allow_users_to_change_password = true
  max_password_age               = 90
  password_reuse_prevention      = 24
}

# PASS: IAM user without inline policies
resource "aws_iam_user" "managed_policies_only" {
  name = "managed-policies-user"

  tags = {
    Department = "Healthcare"
  }
}

# ============================================================================
# AUDIT LOGGING RULES - Passing Examples
# ============================================================================

# PASS: CloudTrail with logging and validation enabled
resource "aws_cloudtrail" "hipaa_trail" {
  name                          = "hipaa-audit-trail"
  s3_bucket_name                = "cloudtrail-logs-bucket"
  enable_logging                = true
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_log_file_validation    = true

  tags = {
    Purpose = "HIPAA-Audit"
  }
}

# PASS: S3 bucket with access logging
resource "aws_s3_bucket_logging" "phi_bucket_logging" {
  bucket = aws_s3_bucket.phi_encrypted.id

  target_bucket = "s3-access-logs-bucket"
  target_prefix = "phi-bucket-logs/"
}

# PASS: CloudWatch log group with adequate retention
resource "aws_cloudwatch_log_group" "hipaa_logs" {
  name              = "/aws/hipaa/application"
  retention_in_days = 365

  tags = {
    Purpose = "HIPAA-Audit"
  }
}

# ============================================================================
# NETWORK SECURITY RULES - Passing Examples
# ============================================================================

# PASS: VPC Flow Logs enabled
resource "aws_flow_log" "vpc_flow_logs" {
  vpc_id          = "vpc-12345"
  traffic_type    = "ALL"
  iam_role_arn    = "arn:aws:iam::123456789012:role/flow-logs-role"
  log_destination = "arn:aws:logs:us-east-1:123456789012:log-group:vpc-flow-logs"
}

# PASS: Security group with restricted access
resource "aws_security_group" "restricted_sg" {
  name        = "restricted-sg"
  description = "Security group with restricted access"
  vpc_id      = "vpc-12345"

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
    description = "HTTPS from internal network only"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "restricted-security-group"
  }
}

# PASS: Network ACL with ingress restrictions
resource "aws_network_acl" "restricted_nacl" {
  vpc_id = "vpc-12345"

  ingress {
    protocol   = "tcp"
    rule_no    = 100
    action     = "allow"
    cidr_block = "10.0.0.0/8"
    from_port  = 443
    to_port    = 443
  }

  egress {
    protocol   = "-1"
    rule_no    = 100
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 0
    to_port    = 0
  }

  tags = {
    Name = "restricted-nacl"
  }
}

# PASS: RDS with parameter group (for SSL enforcement)
resource "aws_db_parameter_group" "ssl_required" {
  name   = "rds-ssl-required"
  family = "postgres13"

  parameter {
    name  = "rds.force_ssl"
    value = "1"
  }
}

# PASS: Elasticsearch in VPC
resource "aws_elasticsearch_domain" "vpc_es" {
  domain_name           = "hipaa-elasticsearch"
  elasticsearch_version = "7.10"

  cluster_config {
    instance_type = "t3.medium.elasticsearch"
  }

  vpc_options {
    subnet_ids         = ["subnet-12345"]
    security_group_ids = ["sg-12345"]
  }

  ebs_options {
    ebs_enabled = true
    volume_size = 100
  }

  encrypt_at_rest {
    enabled = true
  }

  node_to_node_encryption {
    enabled = true
  }

  tags = {
    Environment = "production"
  }
}

# PASS: Lambda function with PHI tag in VPC
resource "aws_lambda_function" "phi_processor" {
  filename      = "lambda.zip"
  function_name = "phi-processor"
  role          = "arn:aws:iam::123456789012:role/lambda-role"
  handler       = "index.handler"
  runtime       = "python3.9"

  vpc_config {
    subnet_ids         = ["subnet-12345", "subnet-67890"]
    security_group_ids = ["sg-12345"]
  }

  tags = {
    DataClassification = "PHI"
  }
}

# ============================================================================
# BACKUP AND RECOVERY RULES - Passing Examples
# ============================================================================

# PASS: S3 bucket versioning for PHI
resource "aws_s3_bucket_versioning" "phi_versioning" {
  bucket = aws_s3_bucket.phi_encrypted.id

  versioning_configuration {
    status = "Enabled"
  }
}

# PASS: DynamoDB with point-in-time recovery
resource "aws_dynamodb_table" "phi_table" {
  name           = "phi-records"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "PatientId"

  attribute {
    name = "PatientId"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }

  server_side_encryption {
    enabled = true
  }

  tags = {
    DataClassification = "PHI"
  }
}

# PASS: EBS snapshot with encryption
resource "aws_ebs_snapshot" "encrypted_snapshot" {
  volume_id = aws_ebs_volume.encrypted_volume.id
  encrypted = true

  tags = {
    Name = "encrypted-backup"
  }
}

# ============================================================================
# FAILING EXAMPLES
# ============================================================================

# FAIL: S3 bucket with PHI tag but no encryption
resource "aws_s3_bucket" "phi_unencrypted" {
  bucket = "healthcare-phi-data-unencrypted"

  tags = {
    DataClassification = "PHI"
    Environment        = "production"
  }
}

# FAIL: RDS with PHI tag but no encryption
resource "aws_db_instance" "phi_database_unencrypted" {
  identifier          = "healthcare-phi-db-unencrypted"
  engine              = "postgres"
  instance_class      = "db.t3.medium"
  allocated_storage   = 100
  storage_encrypted   = false
  publicly_accessible = true

  tags = {
    DataClassification = "PHI"
  }
}

# FAIL: EBS volume without encryption
resource "aws_ebs_volume" "unencrypted_volume" {
  availability_zone = "us-east-1a"
  size              = 100
  encrypted         = false

  tags = {
    Name = "unencrypted-ebs-volume"
  }
}

# FAIL: EC2 instance without encrypted root volume
resource "aws_instance" "unencrypted_instance" {
  ami           = "ami-12345678"
  instance_type = "t3.medium"

  root_block_device {
    encrypted = false
  }

  tags = {
    Name = "unencrypted-instance"
  }
}

# FAIL: KMS key without rotation
resource "aws_kms_key" "no_rotation" {
  description             = "KMS key without rotation"
  enable_key_rotation     = false
  deletion_window_in_days = 30
}

# FAIL: ALB with HTTP listener
resource "aws_lb_listener" "http_listener" {
  load_balancer_arn = aws_lb.application.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.main.arn
  }
}

# FAIL: ElastiCache without encryption at rest
resource "aws_elasticache_replication_group" "unencrypted_cache" {
  replication_group_id       = "unencrypted-cache"
  replication_group_description = "Cache without encryption"
  engine                     = "redis"
  node_type                  = "cache.t3.medium"
  number_cache_clusters      = 2
  at_rest_encryption_enabled = false
  transit_encryption_enabled = false
}

# FAIL: Redshift without encryption
resource "aws_redshift_cluster" "unencrypted_warehouse" {
  cluster_identifier  = "unencrypted-warehouse"
  database_name       = "healthcare"
  master_username     = "admin"
  master_password     = "SecurePassword123!"
  node_type           = "dc2.large"
  cluster_type        = "single-node"
  encrypted           = false
  publicly_accessible = true
}

# FAIL: IAM user with force_destroy
resource "aws_iam_user" "force_destroy_user" {
  name          = "force-destroy-user"
  force_destroy = true
}

# FAIL: IAM policy with wildcard actions
resource "aws_iam_policy" "wildcard_policy" {
  name        = "wildcard-policy"
  description = "Policy with wildcard actions"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "*"
        Resource = "*"
      }
    ]
  })
}

# FAIL: S3 bucket without public access block
resource "aws_s3_bucket" "no_public_block" {
  bucket = "no-public-block-bucket"

  tags = {
    Environment = "production"
  }
}

# FAIL: EC2 instance with PHI tag and public IP
resource "aws_instance" "phi_public_instance" {
  ami                         = "ami-12345678"
  instance_type               = "t3.medium"
  associate_public_ip_address = true

  tags = {
    DataClassification = "PHI"
  }
}

# FAIL: IAM password policy with weak requirements
resource "aws_iam_account_password_policy" "weak" {
  minimum_password_length        = 8
  require_uppercase_characters   = false
  require_lowercase_characters   = false
  require_numbers                = false
  require_symbols                = false
}

# FAIL: IAM user with inline policies
resource "aws_iam_user" "inline_policies_user" {
  name = "inline-policies-user"

  inline_policy {
    name = "inline-policy"

    policy = jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Effect   = "Allow"
          Action   = "s3:*"
          Resource = "*"
        }
      ]
    })
  }
}

# FAIL: CloudTrail without log validation
resource "aws_cloudtrail" "no_validation" {
  name                          = "no-validation-trail"
  s3_bucket_name                = "cloudtrail-logs-bucket"
  enable_logging                = true
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_log_file_validation    = false
}

# FAIL: RDS without audit logging
resource "aws_db_instance" "no_logging" {
  identifier        = "no-logging-db"
  engine            = "postgres"
  instance_class    = "db.t3.medium"
  allocated_storage = 100
  storage_encrypted = true
}

# FAIL: CloudWatch log group with insufficient retention
resource "aws_cloudwatch_log_group" "short_retention" {
  name              = "/aws/short-retention"
  retention_in_days = 30
}

# FAIL: Security group with wide-open access
resource "aws_security_group" "wide_open_sg" {
  name        = "wide-open-sg"
  description = "Security group with unrestricted access"
  vpc_id      = "vpc-12345"

  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# FAIL: Network ACL without ingress restrictions
resource "aws_network_acl" "no_restrictions" {
  vpc_id = "vpc-12345"

  tags = {
    Name = "no-restrictions-nacl"
  }
}

# FAIL: Elasticsearch not in VPC
resource "aws_elasticsearch_domain" "public_es" {
  domain_name           = "public-elasticsearch"
  elasticsearch_version = "7.10"

  cluster_config {
    instance_type = "t3.medium.elasticsearch"
  }

  ebs_options {
    ebs_enabled = true
    volume_size = 100
  }
}

# FAIL: Lambda function with PHI tag not in VPC
resource "aws_lambda_function" "phi_processor_public" {
  filename      = "lambda.zip"
  function_name = "phi-processor-public"
  role          = "arn:aws:iam::123456789012:role/lambda-role"
  handler       = "index.handler"
  runtime       = "python3.9"

  tags = {
    DataClassification = "PHI"
  }
}

# FAIL: RDS with insufficient backup retention
resource "aws_db_instance" "short_backup" {
  identifier              = "short-backup-db"
  engine                  = "postgres"
  instance_class          = "db.t3.medium"
  allocated_storage       = 100
  storage_encrypted       = true
  backup_retention_period = 3
}

# FAIL: DynamoDB without point-in-time recovery
resource "aws_dynamodb_table" "no_pitr" {
  name         = "no-pitr-table"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "Id"

  attribute {
    name = "Id"
    type = "S"
  }

  point_in_time_recovery {
    enabled = false
  }
}

# FAIL: EBS snapshot without encryption
resource "aws_ebs_snapshot" "unencrypted_snapshot" {
  volume_id = aws_ebs_volume.unencrypted_volume.id
  encrypted = false

  tags = {
    Name = "unencrypted-backup"
  }
}
