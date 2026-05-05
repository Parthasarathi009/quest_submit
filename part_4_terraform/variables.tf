# Variables for Terraform configuration

variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "s3_bucket_name" {
  description = "Base name for S3 bucket (account ID will be appended)"
  type        = string
  default     = "rearc-quest-data"
}

variable "lambda_timeout" {
  description = "Timeout for Lambda functions in seconds"
  type        = number
  default     = 300
}

variable "lambda_memory" {
  description = "Memory allocation for Lambda functions in MB"
  type        = number
  default     = 512
}

variable "tags" {
  description = "Common tags to apply to resources"
  type        = map(string)
  default = {
    Project     = "rearc-quest"
    ManagedBy   = "Terraform"
  }
}
