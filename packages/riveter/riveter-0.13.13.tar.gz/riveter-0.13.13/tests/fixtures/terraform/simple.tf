resource "aws_instance" "web_server" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"

  tags = {
    Name        = "web-server"
    Environment = "production"
    CostCenter  = "12345"
  }

  root_block_device {
    volume_size = 20
    volume_type = "gp3"
  }

  security_groups = ["sg-12345678"]
}

resource "aws_s3_bucket" "storage" {
  bucket = "my-test-bucket"

  tags = {
    Environment = "production"
    Purpose     = "data-storage"
  }
}

resource "aws_rds_instance" "database" {
  engine         = "mysql"
  engine_version = "8.0"
  instance_class = "db.t3.micro"
  allocated_storage = 20

  tags = {
    Environment = "production"
    Name        = "database"
  }
}
