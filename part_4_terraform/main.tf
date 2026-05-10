# Main Terraform configuration for Rearc Data Quest

terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Uncomment to use S3 backend for state management
  # backend "s3" {
  #   bucket         = "your-terraform-state-bucket"
  #   key            = "rearc-quest/terraform.tfstate"
  #   region         = "us-east-1"
  #   encrypt        = true
  #   dynamodb_table = "terraform-locks"
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "rearc-quest"
      Environment = var.environment
      CreatedBy   = "Terraform"
    }
  }
}

# Data source for current AWS account
data "aws_caller_identity" "current" {}

# S3 Bucket for data storage
resource "aws_s3_bucket" "data_bucket" {
  bucket = "${var.s3_bucket_name}-${data.aws_caller_identity.current.account_id}"

  tags = {
    Name = "rearc-quest-data-bucket"
  }
}

# Enable versioning
resource "aws_s3_bucket_versioning" "data_bucket_versioning" {
  bucket = aws_s3_bucket.data_bucket.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Block public access
resource "aws_s3_bucket_public_access_block" "data_bucket_pab" {
  bucket = aws_s3_bucket.data_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# S3 Bucket notification for SQS
resource "aws_s3_bucket_notification" "data_bucket_notification" {
  bucket = aws_s3_bucket.data_bucket.id

  queue {
    filter_prefix = "population_data/"
    filter_suffix = ".json"
    events        = ["s3:ObjectCreated:*"]
    queue_arn     = aws_sqs_queue.analytics_queue.arn
  }

  depends_on = [aws_sqs_queue_policy.analytics_queue_policy]
}

# SQS Queue for analytics processing
resource "aws_sqs_queue" "analytics_queue" {
  name                       = "rearc-quest-analytics-queue"
  delay_seconds              = 0
  max_message_size           = 262144
  message_retention_seconds  = 1209600 # 14 days
  receive_wait_time_seconds  = 20
  visibility_timeout_seconds = 300

  tags = {
    Name = "rearc-quest-analytics-queue"
  }
}

# SQS Queue Policy to allow S3 to send messages
resource "aws_sqs_queue_policy" "analytics_queue_policy" {
  queue_url = aws_sqs_queue.analytics_queue.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "s3.amazonaws.com"
        }
        Action   = "sqs:SendMessage"
        Resource = aws_sqs_queue.analytics_queue.arn
        Condition = {
          ArnEquals = {
            "aws:SourceArn" = aws_s3_bucket.data_bucket.arn
          }
        }
      }
    ]
  })
}

# CloudWatch Log Group for Lambda
resource "aws_cloudwatch_log_group" "combined_lambda_logs" {
  name              = "/aws/lambda/rearc-quest-combined-data-pipeline"
  retention_in_days = 30

  tags = {
    Name = "rearc-quest-combined-lambda-logs"
  }
}

resource "aws_cloudwatch_log_group" "analytics_lambda_logs" {
  name              = "/aws/lambda/rearc-quest-analytics"
  retention_in_days = 30

  tags = {
    Name = "rearc-quest-analytics-lambda-logs"
  }
}

# IAM Role for Lambda functions
resource "aws_iam_role" "lambda_role" {
  name = "rearc-quest-lambda-role"

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

# IAM Policy for Lambda to access S3 and CloudWatch
resource "aws_iam_role_policy" "lambda_policy" {
  name = "rearc-quest-lambda-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket",
          "s3:HeadBucket"
          # CHANGE 1 (was line ~168): REMOVED "s3:CreateBucket"
          # Lambda should never create buckets — Terraform owns that.
          # This was causing a second unexpected S3 bucket to appear
          # when the Lambda function ran and called create_bucket().
        ]
        Resource = [
          aws_s3_bucket.data_bucket.arn,
          "${aws_s3_bucket.data_bucket.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ]
        Resource = aws_sqs_queue.analytics_queue.arn
      }
    ]
  })
}

# CHANGE 2 (was line ~201): NEW resource — upload the layer zip to S3 first.
# AWS Lambda's direct upload limit is ~67MB (70167211 bytes).
# Uploading via S3 bypasses that limit (up to 250MB unzipped is allowed).
# This resource must be created BEFORE the layer version below.
resource "aws_s3_object" "lambda_layer_zip" {
  bucket = aws_s3_bucket.data_bucket.id
  key    = "lambda-layers/python_dependencies.zip"
  source = "python_dependencies.zip"
  etag   = filemd5("python_dependencies.zip")  # triggers re-upload only when zip actually changes
}

# Lambda Layer for Python dependencies
# CHANGE 3 (was line ~201-210): Replaced filename-based upload with S3-based upload.
#
# REMOVED:
#   filename         = "python_dependencies.zip"
#   source_code_hash = filebase64sha256("python_dependencies.zip")
#   lifecycle { ignore_changes = [filename, source_code_hash] }
#     ^^^ This was silently preventing layer updates on every terraform apply
#
# ADDED:
#   s3_bucket  = pointing to the data bucket
#   s3_key     = pointing to the object uploaded above
#   depends_on = ensures the zip is in S3 before the layer is created
resource "aws_lambda_layer_version" "dependencies" {
  s3_bucket           = aws_s3_bucket.data_bucket.id
  s3_key              = aws_s3_object.lambda_layer_zip.key
  layer_name          = "rearc-quest-dependencies"
  compatible_runtimes = ["python3.11"]

  depends_on = [aws_s3_object.lambda_layer_zip]
}

# Lambda Function for combined data pipeline (Part 1 & 2)
resource "aws_lambda_function" "combined_pipeline" {
  filename      = "combined_lambda.zip"
  function_name = "rearc-quest-combined-data-pipeline"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_functions.combined_lambda.lambda_handler"
  runtime       = "python3.11"
  timeout       = 300
  memory_size   = 512

  environment {
    variables = {
      S3_BUCKET = aws_s3_bucket.data_bucket.id
    }
  }

  layers = [aws_lambda_layer_version.dependencies.arn]

  depends_on = [
    aws_iam_role_policy.lambda_policy,
    aws_cloudwatch_log_group.combined_lambda_logs
  ]
}

# Lambda Function for analytics (Part 3)
resource "aws_lambda_function" "analytics" {
  filename      = "analytics_lambda.zip"
  function_name = "rearc-quest-analytics"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_functions.analytics_lambda.lambda_handler"
  runtime       = "python3.11"
  timeout       = 300
  memory_size   = 512

  environment {
    variables = {
      S3_BUCKET = aws_s3_bucket.data_bucket.id
    }
  }

  layers = [aws_lambda_layer_version.dependencies.arn]

  depends_on = [
    aws_iam_role_policy.lambda_policy,
    aws_cloudwatch_log_group.analytics_lambda_logs
  ]
}

# SQS Event Source Mapping for Analytics Lambda
resource "aws_lambda_event_source_mapping" "sqs_to_lambda" {
  event_source_arn = aws_sqs_queue.analytics_queue.arn
  function_name    = aws_lambda_function.analytics.arn
  batch_size       = 10

  # Only process messages when function completes
  function_response_types = ["ReportBatchItemFailures"]
}

# EventBridge Rule for daily scheduled execution (2 AM UTC)
resource "aws_cloudwatch_event_rule" "daily_schedule" {
  name                = "rearc-quest-daily-schedule"
  description         = "Trigger combined data pipeline daily at 2 AM UTC"
  schedule_expression = "cron(0 2 * * ? *)"
}

# EventBridge Target - Combined Lambda
resource "aws_cloudwatch_event_target" "combined_pipeline_target" {
  rule      = aws_cloudwatch_event_rule.daily_schedule.name
  target_id = "CombinedPipelineLambda"
  arn       = aws_lambda_function.combined_pipeline.arn
}

# Lambda Permission for EventBridge
resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.combined_pipeline.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily_schedule.arn
}

# CloudWatch Alarms
resource "aws_cloudwatch_metric_alarm" "combined_lambda_errors" {
  alarm_name          = "rearc-quest-combined-lambda-errors"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = "1"
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Sum"
  threshold           = "1"
  alarm_description   = "Alert when combined pipeline Lambda has errors"
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = aws_lambda_function.combined_pipeline.function_name
  }
}

resource "aws_cloudwatch_metric_alarm" "analytics_lambda_errors" {
  alarm_name          = "rearc-quest-analytics-lambda-errors"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = "1"
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Sum"
  threshold           = "1"
  alarm_description   = "Alert when analytics Lambda has errors"
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = aws_lambda_function.analytics.function_name
  }
}
