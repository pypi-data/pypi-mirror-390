# Input variables for the S3 bucket example

variable "bucket_name" {
  description = "Name of the S3 bucket to create"
  type        = string
  default     = "riveter-example-bucket-12345"

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9-]*[a-z0-9]$", var.bucket_name))
    error_message = "Bucket name must be lowercase, start and end with alphanumeric characters, and contain only letters, numbers, and hyphens."
  }

  validation {
    condition     = length(var.bucket_name) >= 3 && length(var.bucket_name) <= 63
    error_message = "Bucket name must be between 3 and 63 characters long."
  }
}

variable "environment" {
  description = "Environment name for resource tagging"
  type        = string
  default     = "learning"

  validation {
    condition     = contains(["development", "staging", "production", "learning"], var.environment)
    error_message = "Environment must be one of: development, staging, production, learning."
  }
}