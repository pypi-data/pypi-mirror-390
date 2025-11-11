resource "aws_instance" "broken_instance" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"

  tags = {
    Name        = "broken-instance"
    Environment = "test"
    # Missing closing brace intentionally

  security_groups = ["sg-12345678"]
}

# Missing resource block closing brace
