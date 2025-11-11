# AWS PCI-DSS Compliance Test Fixtures
# This file contains both passing and failing examples for aws-pci-dss rule pack

# ============================================================================
# NETWORK SEGMENTATION RULES TEST FIXTURES
# ============================================================================

# PASS: Security group with restricted access for PCI scope
resource "aws_security_group" "pci_compliant_sg" {
  name        = "pci-compliant-sg"
  description = "Security group for PCI compliant resources with restricted access"
  vpc_id      = aws_vpc.pci_vpc.id

  ingress {
    description = "HTTPS from corporate network"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
  }

  ingress {
    description = "SSH from bastion host"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["10.0.1.0/24"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name     = "pci-compliant-sg"
    PCIScope = "true"
  }
}

# FAIL: Security group allowing unrestricted access from internet
resource "aws_security_group" "pci_unrestricted_sg" {
  name        = "pci-unrestricted-sg"
  description = "Security group with unrestricted access - PCI violation"
  vpc_id      = aws_vpc.pci_vpc.id

  ingress {
    description = "All traffic from internet"
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name     = "pci-unrestricted-sg"
    PCIScope = "true"
  }
}

# FAIL: Security group allowing SSH from internet
resource "aws_security_group" "pci_ssh_internet_sg" {
  name        = "pci-ssh-internet-sg"
  description = "Security group allowing SSH from internet - PCI violation"
  vpc_id      = aws_vpc.pci_vpc.id

  ingress {
    description = "SSH from internet"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name     = "pci-ssh-internet-sg"
    PCIScope = "true"
  }
}

# FAIL: Security group allowing RDP from internet
resource "aws_security_group" "pci_rdp_internet_sg" {
  name        = "pci-rdp-internet-sg"
  description = "Security group allowing RDP from internet - PCI violation"
  vpc_id      = aws_vpc.pci_vpc.id

  ingress {
    description = "RDP from internet"
    from_port   = 3389
    to_port     = 3389
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name     = "pci-rdp-internet-sg"
    PCIScope = "true"
  }
}

# PASS: Network ACL with default deny policy
resource "aws_network_acl" "pci_compliant_nacl" {
  vpc_id = aws_vpc.pci_vpc.id

  ingress {
    protocol   = "tcp"
    rule_no    = 100
    action     = "allow"
    cidr_block = "10.0.0.0/8"
    from_port  = 443
    to_port    = 443
  }

  ingress {
    protocol   = "-1"
    rule_no    = 32767
    action     = "deny"
    cidr_block = "0.0.0.0/0"
  }

  egress {
    protocol   = "-1"
    rule_no    = 100
    action     = "allow"
    cidr_block = "0.0.0.0/0"
  }

  egress {
    protocol   = "-1"
    rule_no    = 32767
    action     = "deny"
    cidr_block = "0.0.0.0/0"
  }

  tags = {
    Name     = "pci-compliant-nacl"
    PCIScope = "true"
  }
}

# PASS: VPC Flow Logs enabled
resource "aws_flow_log" "pci_vpc_flow_log" {
  iam_role_arn    = aws_iam_role.flow_log_role.arn
  log_destination = aws_cloudwatch_log_group.pci_flow_log_group.arn
  traffic_type    = "ALL"
  vpc_id          = aws_vpc.pci_vpc.id
}

# PASS: Application Load Balancer with WAF enabled (indicated by tag)
resource "aws_lb" "pci_alb_with_waf" {
  name               = "pci-alb-with-waf"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.pci_compliant_sg.id]
  subnets            = [aws_subnet.pci_public_subnet_1.id, aws_subnet.pci_public_subnet_2.id]

  enable_deletion_protection = true

  access_logs {
    bucket  = aws_s3_bucket.pci_alb_logs.bucket
    prefix  = "alb-logs"
    enabled = true
  }

  tags = {
    Name       = "pci-alb-with-waf"
    PCIScope   = "true"
    WAFEnabled = "true"
  }
}

# FAIL: Application Load Balancer without WAF enabled
resource "aws_lb" "pci_alb_no_waf" {
  name               = "pci-alb-no-waf"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.pci_compliant_sg.id]
  subnets            = [aws_subnet.pci_public_subnet_1.id, aws_subnet.pci_public_subnet_2.id]

  tags = {
    Name     = "pci-alb-no-waf"
    PCIScope = "true"
  }
}

# FAIL: RDS instance with public access in PCI scope
resource "aws_db_instance" "pci_rds_public" {
  identifier     = "pci-rds-public"
  engine         = "mysql"
  engine_version = "8.0"
  instance_class = "db.t3.micro"
  allocated_storage = 20

  db_name  = "pcidb"
  username = "admin"
  password = "password123"

  publicly_accessible = true
  storage_encrypted   = true

  tags = {
    Name     = "pci-rds-public"
    PCIScope = "true"
  }
}

# FAIL: EC2 instance with public IP in PCI scope
resource "aws_instance" "pci_ec2_public_ip" {
  ami                         = "ami-0c02fb55956c7d316"
  instance_type               = "t3.micro"
  subnet_id                   = aws_subnet.pci_public_subnet_1.id
  associate_public_ip_address = true
  vpc_security_group_ids      = [aws_security_group.pci_compliant_sg.id]

  root_block_device {
    encrypted = true
  }

  tags = {
    Name     = "pci-ec2-public-ip"
    PCIScope = "true"
  }
}

# PASS: ElastiCache in private subnet group
resource "aws_elasticache_replication_group" "pci_elasticache_private" {
  replication_group_id       = "pci-elasticache"
  description                = "PCI compliant ElastiCache cluster"
  port                       = 6379
  parameter_group_name       = "default.redis7"
  node_type                  = "cache.t3.micro"
  num_cache_clusters         = 2
  subnet_group_name          = aws_elasticache_subnet_group.pci_cache_subnet_group.name
  security_group_ids         = [aws_security_group.pci_compliant_sg.id]

  at_rest_encryption_enabled = true
  transit_encryption_enabled = true

  tags = {
    Name     = "pci-elasticache-private"
    PCIScope = "true"
  }
}

# FAIL: Redshift cluster with public access
resource "aws_redshift_cluster" "pci_redshift_public" {
  cluster_identifier      = "pci-redshift-public"
  database_name           = "pcidb"
  master_username         = "admin"
  master_password         = "Password123"
  node_type               = "dc2.large"
  cluster_type            = "single-node"
  publicly_accessible     = true
  encrypted               = true

  tags = {
    Name     = "pci-redshift-public"
    PCIScope = "true"
  }
}

# ============================================================================
# ENCRYPTION RULES TEST FIXTURES
# ============================================================================

# PASS: S3 bucket with encryption for cardholder data
resource "aws_s3_bucket" "pci_cardholder_data_encrypted" {
  bucket = "pci-cardholder-data-encrypted-12345"

  tags = {
    Name     = "pci-cardholder-data-encrypted"
    PCIScope = "true"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "pci_cardholder_data_encryption" {
  bucket = aws_s3_bucket.pci_cardholder_data_encrypted.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.pci_s3_key.arn
      sse_algorithm     = "aws:kms"
    }
  }
}

# FAIL: S3 bucket without encryption for cardholder data
resource "aws_s3_bucket" "pci_cardholder_data_unencrypted" {
  bucket = "pci-cardholder-data-unencrypted-12345"

  tags = {
    Name     = "pci-cardholder-data-unencrypted"
    PCIScope = "true"
  }
}

# PASS: RDS instance with encryption for cardholder data
resource "aws_db_instance" "pci_rds_encrypted" {
  identifier     = "pci-rds-encrypted"
  engine         = "mysql"
  engine_version = "8.0"
  instance_class = "db.t3.micro"
  allocated_storage = 20

  db_name  = "pcidb"
  username = "admin"
  password = "password123"

  publicly_accessible = false
  storage_encrypted   = true
  kms_key_id         = aws_kms_key.pci_rds_key.arn

  tags = {
    Name     = "pci-rds-encrypted"
    PCIScope = "true"
  }
}

# FAIL: RDS instance without encryption for cardholder data
resource "aws_db_instance" "pci_rds_unencrypted" {
  identifier     = "pci-rds-unencrypted"
  engine         = "mysql"
  engine_version = "8.0"
  instance_class = "db.t3.micro"
  allocated_storage = 20

  db_name  = "pcidb"
  username = "admin"
  password = "password123"

  publicly_accessible = false
  storage_encrypted   = false

  tags = {
    Name     = "pci-rds-unencrypted"
    PCIScope = "true"
  }
}

# PASS: EBS volume with encryption in PCI scope
resource "aws_ebs_volume" "pci_ebs_encrypted" {
  availability_zone = "us-east-1a"
  size              = 40
  encrypted         = true
  kms_key_id        = aws_kms_key.pci_ebs_key.arn

  tags = {
    Name     = "pci-ebs-encrypted"
    PCIScope = "true"
  }
}

# FAIL: EBS volume without encryption in PCI scope
resource "aws_ebs_volume" "pci_ebs_unencrypted" {
  availability_zone = "us-east-1a"
  size              = 40
  encrypted         = false

  tags = {
    Name     = "pci-ebs-unencrypted"
    PCIScope = "true"
  }
}

# PASS: KMS key with automatic rotation enabled
resource "aws_kms_key" "pci_s3_key" {
  description             = "KMS key for PCI S3 encryption"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  tags = {
    Name = "pci-s3-key"
  }
}

resource "aws_kms_key" "pci_rds_key" {
  description             = "KMS key for PCI RDS encryption"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  tags = {
    Name = "pci-rds-key"
  }
}

resource "aws_kms_key" "pci_ebs_key" {
  description             = "KMS key for PCI EBS encryption"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  tags = {
    Name = "pci-ebs-key"
  }
}

# FAIL: KMS key without automatic rotation
resource "aws_kms_key" "pci_key_no_rotation" {
  description             = "KMS key without rotation"
  deletion_window_in_days = 7
  enable_key_rotation     = false

  tags = {
    Name = "pci-key-no-rotation"
  }
}

# PASS: CloudFront distribution with HTTPS enforcement
resource "aws_cloudfront_distribution" "pci_cloudfront_https" {
  origin {
    domain_name = aws_s3_bucket.pci_cardholder_data_encrypted.bucket_regional_domain_name
    origin_id   = "S3-pci-cardholder-data"

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.pci_oai.cloudfront_access_identity_path
    }
  }

  enabled = true

  default_cache_behavior {
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-pci-cardholder-data"

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
  }

  viewer_certificate {
    cloudfront_default_certificate = true
    minimum_protocol_version       = "TLSv1.2_2021"
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  tags = {
    Name     = "pci-cloudfront-https"
    PCIScope = "true"
  }
}

# FAIL: CloudFront distribution without HTTPS enforcement
resource "aws_cloudfront_distribution" "pci_cloudfront_no_https" {
  origin {
    domain_name = aws_s3_bucket.pci_cardholder_data_encrypted.bucket_regional_domain_name
    origin_id   = "S3-pci-cardholder-data"

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.pci_oai.cloudfront_access_identity_path
    }
  }

  enabled = true

  default_cache_behavior {
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-pci-cardholder-data"

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "allow-all"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }

  viewer_certificate {
    cloudfront_default_certificate = true
    minimum_protocol_version       = "TLSv1"
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  tags = {
    Name     = "pci-cloudfront-no-https"
    PCIScope = "true"
  }
}

# PASS: ALB listener with HTTPS and proper SSL policy
resource "aws_lb_listener" "pci_alb_https_listener" {
  load_balancer_arn = aws_lb.pci_alb_with_waf.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn   = aws_acm_certificate.pci_cert.arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.pci_tg.arn
  }

  tags = {
    Name     = "pci-alb-https-listener"
    PCIScope = "true"
  }
}

# FAIL: ALB listener with HTTP protocol
resource "aws_lb_listener" "pci_alb_http_listener" {
  load_balancer_arn = aws_lb.pci_alb_no_waf.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.pci_tg.arn
  }

  tags = {
    Name     = "pci-alb-http-listener"
    PCIScope = "true"
  }
}

# PASS: DynamoDB table with encryption at rest
resource "aws_dynamodb_table" "pci_dynamodb_encrypted" {
  name           = "pci-dynamodb-encrypted"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"

  attribute {
    name = "id"
    type = "S"
  }

  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.pci_dynamodb_key.arn
  }

  tags = {
    Name     = "pci-dynamodb-encrypted"
    PCIScope = "true"
  }
}

# FAIL: DynamoDB table without encryption at rest
resource "aws_dynamodb_table" "pci_dynamodb_unencrypted" {
  name           = "pci-dynamodb-unencrypted"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"

  attribute {
    name = "id"
    type = "S"
  }

  tags = {
    Name     = "pci-dynamodb-unencrypted"
    PCIScope = "true"
  }
}

# ============================================================================
# ACCESS CONTROL RULES TEST FIXTURES
# ============================================================================

# PASS: IAM user with MFA requirement (indicated by tag)
resource "aws_iam_user" "pci_user_with_mfa" {
  name = "pci-user-with-mfa"
  path = "/pci/"

  force_destroy = false

  tags = {
    Name      = "pci-user-with-mfa"
    PCIAccess = "true"
    MFAEnabled = "true"
  }
}

# FAIL: IAM user without MFA requirement
resource "aws_iam_user" "pci_user_no_mfa" {
  name = "pci-user-no-mfa"
  path = "/pci/"

  force_destroy = true

  tags = {
    Name      = "pci-user-no-mfa"
    PCIAccess = "true"
  }
}

# PASS: IAM policy following least privilege
resource "aws_iam_policy" "pci_least_privilege_policy" {
  name        = "pci-least-privilege-policy"
  path        = "/pci/"
  description = "PCI compliant policy with least privilege"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Effect   = "Allow"
        Resource = "arn:aws:s3:::pci-bucket/*"
      }
    ]
  })
}

# FAIL: IAM policy with wildcard actions
resource "aws_iam_policy" "pci_wildcard_policy" {
  name        = "pci-wildcard-policy"
  path        = "/pci/"
  description = "PCI non-compliant policy with wildcard actions"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = "*"
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

# PASS: S3 bucket public access block
resource "aws_s3_bucket_public_access_block" "pci_bucket_pab" {
  bucket = aws_s3_bucket.pci_cardholder_data_encrypted.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# PASS: IAM account password policy with strong requirements
resource "aws_iam_account_password_policy" "pci_password_policy" {
  minimum_password_length        = 14
  require_lowercase_characters   = true
  require_numbers               = true
  require_uppercase_characters   = true
  require_symbols               = true
  allow_users_to_change_password = true
  max_password_age              = 90
  password_reuse_prevention     = 12
}

# PASS: IAM user without inline policies
resource "aws_iam_user" "pci_user_no_inline" {
  name = "pci-user-no-inline"
  path = "/pci/"

  tags = {
    Name = "pci-user-no-inline"
  }
}

# FAIL: IAM user with inline policy
resource "aws_iam_user" "pci_user_with_inline" {
  name = "pci-user-with-inline"
  path = "/pci/"

  inline_policy {
    name = "inline-policy"

    policy = jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Action   = "s3:GetObject"
          Effect   = "Allow"
          Resource = "*"
        }
      ]
    })
  }

  tags = {
    Name = "pci-user-with-inline"
  }
}

# FAIL: Root account access key (simulated)
resource "aws_iam_access_key" "pci_root_access_key" {
  user   = "root"
  status = "Active"
}

# PASS: Lambda function with execution role in PCI scope
resource "aws_lambda_function" "pci_lambda_with_role" {
  filename      = "lambda_function_payload.zip"
  function_name = "pci_lambda_with_role"
  role          = aws_iam_role.pci_lambda_role.arn
  handler       = "index.handler"
  runtime       = "python3.9"

  tags = {
    Name     = "pci-lambda-with-role"
    PCIScope = "true"
  }
}

# PASS: EC2 instance with IAM instance profile in PCI scope
resource "aws_instance" "pci_ec2_with_profile" {
  ami                    = "ami-0c02fb55956c7d316"
  instance_type          = "t3.micro"
  subnet_id              = aws_subnet.pci_private_subnet_1.id
  iam_instance_profile   = aws_iam_instance_profile.pci_ec2_profile.name
  vpc_security_group_ids = [aws_security_group.pci_compliant_sg.id]

  root_block_device {
    encrypted = true
  }

  tags = {
    Name     = "pci-ec2-with-profile"
    PCIScope = "true"
  }
}

# FAIL: EC2 instance without IAM instance profile in PCI scope
resource "aws_instance" "pci_ec2_no_profile" {
  ami                    = "ami-0c02fb55956c7d316"
  instance_type          = "t3.micro"
  subnet_id              = aws_subnet.pci_private_subnet_1.id
  vpc_security_group_ids = [aws_security_group.pci_compliant_sg.id]

  root_block_device {
    encrypted = true
  }

  tags = {
    Name     = "pci-ec2-no-profile"
    PCIScope = "true"
  }
}

# ============================================================================
# LOGGING AND MONITORING RULES TEST FIXTURES
# ============================================================================

# PASS: CloudTrail with proper configuration
resource "aws_cloudtrail" "pci_cloudtrail" {
  name                          = "pci-cloudtrail"
  s3_bucket_name               = aws_s3_bucket.pci_cloudtrail_bucket.bucket
  include_global_service_events = true
  is_multi_region_trail        = true
  enable_logging               = true
  enable_log_file_validation   = true

  event_selector {
    read_write_type                 = "All"
    include_management_events       = true
    data_resource {
      type   = "AWS::S3::Object"
      values = ["arn:aws:s3:::pci-cardholder-data-encrypted-12345/*"]
    }
  }

  tags = {
    Name = "pci-cloudtrail"
  }
}

# FAIL: CloudTrail without log file validation
resource "aws_cloudtrail" "pci_cloudtrail_no_validation" {
  name                          = "pci-cloudtrail-no-validation"
  s3_bucket_name               = aws_s3_bucket.pci_cloudtrail_bucket.bucket
  include_global_service_events = true
  is_multi_region_trail        = true
  enable_logging               = true
  enable_log_file_validation   = false

  tags = {
    Name = "pci-cloudtrail-no-validation"
  }
}

# PASS: CloudWatch log group with adequate retention
resource "aws_cloudwatch_log_group" "pci_log_group" {
  name              = "/aws/pci/application"
  retention_in_days = 365

  tags = {
    Name = "pci-log-group"
  }
}

# FAIL: CloudWatch log group with inadequate retention
resource "aws_cloudwatch_log_group" "pci_log_group_short" {
  name              = "/aws/pci/application-short"
  retention_in_days = 30

  tags = {
    Name = "pci-log-group-short"
  }
}

# PASS: S3 bucket access logging
resource "aws_s3_bucket_logging" "pci_s3_logging" {
  bucket = aws_s3_bucket.pci_cardholder_data_encrypted.id

  target_bucket = aws_s3_bucket.pci_access_logs_bucket.id
  target_prefix = "log/"
}

# PASS: GuardDuty detector enabled
resource "aws_guardduty_detector" "pci_guardduty" {
  enable = true

  datasources {
    s3_logs {
      enable = true
    }
    kubernetes {
      audit_logs {
        enable = true
      }
    }
    malware_protection {
      scan_ec2_instance_with_findings {
        ebs_volumes {
          enable = true
        }
      }
    }
  }

  tags = {
    Name = "pci-guardduty"
  }
}

# FAIL: GuardDuty detector disabled
resource "aws_guardduty_detector" "pci_guardduty_disabled" {
  enable = false

  tags = {
    Name = "pci-guardduty-disabled"
  }
}

# PASS: AWS Config configuration recorder
resource "aws_config_configuration_recorder" "pci_config_recorder" {
  name     = "pci-config-recorder"
  role_arn = aws_iam_role.pci_config_role.arn

  recording_group {
    all_supported                 = true
    include_global_resource_types = true
  }
}

# ============================================================================
# VULNERABILITY MANAGEMENT RULES TEST FIXTURES
# ============================================================================

# PASS: SSM patch baseline with critical/high compliance level
resource "aws_ssm_patch_baseline" "pci_patch_baseline" {
  name             = "pci-patch-baseline"
  description      = "PCI compliant patch baseline"
  operating_system = "AMAZON_LINUX_2"

  approved_patches_compliance_level = "CRITICAL"

  approval_rule {
    approve_after_days = 7
    compliance_level   = "HIGH"

    patch_filter {
      key    = "PRODUCT"
      values = ["AmazonLinux2"]
    }

    patch_filter {
      key    = "CLASSIFICATION"
      values = ["Security", "Bugfix", "Critical"]
    }

    patch_filter {
      key    = "SEVERITY"
      values = ["Critical", "Important"]
    }
  }

  tags = {
    Name = "pci-patch-baseline"
  }
}

# FAIL: SSM patch baseline with low compliance level
resource "aws_ssm_patch_baseline" "pci_patch_baseline_low" {
  name             = "pci-patch-baseline-low"
  description      = "PCI non-compliant patch baseline"
  operating_system = "AMAZON_LINUX_2"

  approved_patches_compliance_level = "LOW"

  tags = {
    Name = "pci-patch-baseline-low"
  }
}

# PASS: Inspector assessment target
resource "aws_inspector_assessment_target" "pci_inspector_target" {
  name = "pci-inspector-target"

  resource_group_arn = aws_inspector_resource_group.pci_resource_group.arn
}

# PASS: Security group with description
resource "aws_security_group" "pci_sg_with_description" {
  name        = "pci-sg-with-description"
  description = "Security group for PCI compliant web servers with detailed access controls and monitoring"
  vpc_id      = aws_vpc.pci_vpc.id

  ingress {
    description = "HTTPS from corporate network only"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
  }

  tags = {
    Name = "pci-sg-with-description"
  }
}

# FAIL: Security group with inadequate description
resource "aws_security_group" "pci_sg_short_description" {
  name        = "pci-sg-short"
  description = "Short desc"
  vpc_id      = aws_vpc.pci_vpc.id

  tags = {
    Name = "pci-sg-short-description"
  }
}

# PASS: EC2 instance with detailed monitoring in PCI scope
resource "aws_instance" "pci_ec2_detailed_monitoring" {
  ami                    = "ami-0c02fb55956c7d316"
  instance_type          = "t3.micro"
  subnet_id              = aws_subnet.pci_private_subnet_1.id
  monitoring             = true
  iam_instance_profile   = aws_iam_instance_profile.pci_ec2_profile.name
  vpc_security_group_ids = [aws_security_group.pci_compliant_sg.id]

  root_block_device {
    encrypted = true
  }

  tags = {
    Name     = "pci-ec2-detailed-monitoring"
    PCIScope = "true"
  }
}

# FAIL: EC2 instance without detailed monitoring in PCI scope
resource "aws_instance" "pci_ec2_no_monitoring" {
  ami                    = "ami-0c02fb55956c7d316"
  instance_type          = "t3.micro"
  subnet_id              = aws_subnet.pci_private_subnet_1.id
  monitoring             = false
  iam_instance_profile   = aws_iam_instance_profile.pci_ec2_profile.name
  vpc_security_group_ids = [aws_security_group.pci_compliant_sg.id]

  root_block_device {
    encrypted = true
  }

  tags = {
    Name     = "pci-ec2-no-monitoring"
    PCIScope = "true"
  }
}

# PASS: RDS instance with enhanced monitoring in PCI scope
resource "aws_db_instance" "pci_rds_enhanced_monitoring" {
  identifier     = "pci-rds-enhanced-monitoring"
  engine         = "mysql"
  engine_version = "8.0"
  instance_class = "db.t3.micro"
  allocated_storage = 20

  db_name  = "pcidb"
  username = "admin"
  password = "password123"

  publicly_accessible = false
  storage_encrypted   = true
  monitoring_interval = 60
  monitoring_role_arn = aws_iam_role.pci_rds_monitoring_role.arn

  tags = {
    Name     = "pci-rds-enhanced-monitoring"
    PCIScope = "true"
  }
}

# FAIL: RDS instance without enhanced monitoring in PCI scope
resource "aws_db_instance" "pci_rds_no_monitoring" {
  identifier     = "pci-rds-no-monitoring"
  engine         = "mysql"
  engine_version = "8.0"
  instance_class = "db.t3.micro"
  allocated_storage = 20

  db_name  = "pcidb"
  username = "admin"
  password = "password123"

  publicly_accessible = false
  storage_encrypted   = true
  monitoring_interval = 0

  tags = {
    Name     = "pci-rds-no-monitoring"
    PCIScope = "true"
  }
}

# PASS: Lambda function with dead letter queue in PCI scope
resource "aws_lambda_function" "pci_lambda_with_dlq" {
  filename      = "lambda_function_payload.zip"
  function_name = "pci_lambda_with_dlq"
  role          = aws_iam_role.pci_lambda_role.arn
  handler       = "index.handler"
  runtime       = "python3.9"

  dead_letter_config {
    target_arn = aws_sqs_queue.pci_dlq.arn
  }

  tags = {
    Name     = "pci-lambda-with-dlq"
    PCIScope = "true"
  }
}

# FAIL: Lambda function without dead letter queue in PCI scope
resource "aws_lambda_function" "pci_lambda_no_dlq" {
  filename      = "lambda_function_payload.zip"
  function_name = "pci_lambda_no_dlq"
  role          = aws_iam_role.pci_lambda_role.arn
  handler       = "index.handler"
  runtime       = "python3.9"

  tags = {
    Name     = "pci-lambda-no-dlq"
    PCIScope = "true"
  }
}

# ============================================================================
# SUPPORTING RESOURCES
# ============================================================================

resource "aws_vpc" "pci_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "pci-vpc"
  }
}

resource "aws_subnet" "pci_public_subnet_1" {
  vpc_id            = aws_vpc.pci_vpc.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-east-1a"

  tags = {
    Name = "pci-public-subnet-1"
  }
}

resource "aws_subnet" "pci_public_subnet_2" {
  vpc_id            = aws_vpc.pci_vpc.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "us-east-1b"

  tags = {
    Name = "pci-public-subnet-2"
  }
}

resource "aws_subnet" "pci_private_subnet_1" {
  vpc_id            = aws_vpc.pci_vpc.id
  cidr_block        = "10.0.3.0/24"
  availability_zone = "us-east-1a"

  tags = {
    Name = "pci-private-subnet-1"
  }
}

resource "aws_subnet" "pci_private_subnet_2" {
  vpc_id            = aws_vpc.pci_vpc.id
  cidr_block        = "10.0.4.0/24"
  availability_zone = "us-east-1b"

  tags = {
    Name = "pci-private-subnet-2"
  }
}

resource "aws_elasticache_subnet_group" "pci_cache_subnet_group" {
  name       = "pci-cache-subnet-group"
  subnet_ids = [aws_subnet.pci_private_subnet_1.id, aws_subnet.pci_private_subnet_2.id]
}

resource "aws_s3_bucket" "pci_alb_logs" {
  bucket = "pci-alb-logs-12345"

  tags = {
    Name = "pci-alb-logs"
  }
}

resource "aws_s3_bucket" "pci_cloudtrail_bucket" {
  bucket = "pci-cloudtrail-logs-12345"

  tags = {
    Name = "pci-cloudtrail-bucket"
  }
}

resource "aws_s3_bucket" "pci_access_logs_bucket" {
  bucket = "pci-access-logs-12345"

  tags = {
    Name = "pci-access-logs-bucket"
  }
}

resource "aws_cloudwatch_log_group" "pci_flow_log_group" {
  name              = "/aws/vpc/flowlogs"
  retention_in_days = 365
}

resource "aws_lb_target_group" "pci_tg" {
  name     = "pci-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.pci_vpc.id

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }
}

resource "aws_acm_certificate" "pci_cert" {
  domain_name       = "example.com"
  validation_method = "DNS"

  tags = {
    Name = "pci-cert"
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_cloudfront_origin_access_identity" "pci_oai" {
  comment = "PCI CloudFront OAI"
}

resource "aws_kms_key" "pci_dynamodb_key" {
  description             = "KMS key for PCI DynamoDB encryption"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  tags = {
    Name = "pci-dynamodb-key"
  }
}

resource "aws_iam_role" "flow_log_role" {
  name = "flow-log-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "vpc-flow-logs.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role" "pci_lambda_role" {
  name = "pci-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role" "pci_config_role" {
  name = "pci-config-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "config.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role" "pci_rds_monitoring_role" {
  name = "pci-rds-monitoring-role"

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
}

resource "aws_iam_instance_profile" "pci_ec2_profile" {
  name = "pci-ec2-profile"
  role = aws_iam_role.pci_ec2_role.name
}

resource "aws_iam_role" "pci_ec2_role" {
  name = "pci-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_inspector_resource_group" "pci_resource_group" {
  tags = {
    Name     = "pci-inspector-group"
    PCIScope = "true"
  }
}

resource "aws_sqs_queue" "pci_dlq" {
  name = "pci-dlq"

  tags = {
    Name = "pci-dlq"
  }
}