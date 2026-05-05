# Outputs from Terraform configuration

output "s3_bucket_name" {
  description = "Name of the created S3 bucket"
  value       = aws_s3_bucket.data_bucket.id
}

output "s3_bucket_arn" {
  description = "ARN of the created S3 bucket"
  value       = aws_s3_bucket.data_bucket.arn
}

output "combined_lambda_function_name" {
  description = "Name of the combined data pipeline Lambda function"
  value       = aws_lambda_function.combined_pipeline.function_name
}

output "combined_lambda_function_arn" {
  description = "ARN of the combined data pipeline Lambda function"
  value       = aws_lambda_function.combined_pipeline.arn
}

output "analytics_lambda_function_name" {
  description = "Name of the analytics Lambda function"
  value       = aws_lambda_function.analytics.function_name
}

output "analytics_lambda_function_arn" {
  description = "ARN of the analytics Lambda function"
  value       = aws_lambda_function.analytics.arn
}

output "sqs_queue_url" {
  description = "URL of the SQS queue for analytics processing"
  value       = aws_sqs_queue.analytics_queue.url
}

output "sqs_queue_arn" {
  description = "ARN of the SQS queue for analytics processing"
  value       = aws_sqs_queue.analytics_queue.arn
}

output "eventbridge_rule_name" {
  description = "Name of the EventBridge rule for daily scheduling"
  value       = aws_cloudwatch_event_rule.daily_schedule.name
}

output "combined_log_group" {
  description = "CloudWatch Log Group for combined Lambda function"
  value       = aws_cloudwatch_log_group.combined_lambda_logs.name
}

output "analytics_log_group" {
  description = "CloudWatch Log Group for analytics Lambda function"
  value       = aws_cloudwatch_log_group.analytics_lambda_logs.name
}

output "deployment_info" {
  description = "Summary of deployed resources"
  value = {
    region           = var.aws_region
    s3_bucket        = aws_s3_bucket.data_bucket.id
    combined_lambda  = aws_lambda_function.combined_pipeline.function_name
    analytics_lambda = aws_lambda_function.analytics.function_name
    sqs_queue        = aws_sqs_queue.analytics_queue.name
    schedule         = "Daily at 2 AM UTC"
  }
}
