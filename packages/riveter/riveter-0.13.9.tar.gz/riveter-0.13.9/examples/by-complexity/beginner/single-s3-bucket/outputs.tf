# Output values for the S3 bucket example

output "bucket_name" {
  description = "Name of the created S3 bucket"
  value       = aws_s3_bucket.example.bucket
}

output "bucket_arn" {
  description = "ARN of the created S3 bucket"
  value       = aws_s3_bucket.example.arn
}

output "bucket_domain_name" {
  description = "Domain name of the S3 bucket"
  value       = aws_s3_bucket.example.bucket_domain_name
}

output "versioning_status" {
  description = "Versioning status of the S3 bucket"
  value       = aws_s3_bucket_versioning.example.versioning_configuration[0].status
}

output "encryption_algorithm" {
  description = "Server-side encryption algorithm used"
  value       = aws_s3_bucket_server_side_encryption_configuration.example.rule[0].apply_server_side_encryption_by_default[0].sse_algorithm
}