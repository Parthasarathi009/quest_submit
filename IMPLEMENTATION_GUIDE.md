# Rearc Data Quest - Complete Implementation Guide

This is a complete, production-ready implementation of the Rearc Data Quest assignment. It includes infrastructure-as-code, Lambda functions, data processing pipelines, and analytics.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Project Structure](#project-structure)
5. [Setup Instructions](#setup-instructions)
6. [Deployment](#deployment)
7. [Part 1: BLS Data Sync](#part-1-bls-data-sync)
8. [Part 2: Population API](#part-2-population-api)
9. [Part 3: Data Analytics](#part-3-data-analytics)
10. [Part 4: Infrastructure & Automation](#part-4-infrastructure--automation)
11. [Testing & Validation](#testing--validation)
12. [Monitoring & Troubleshooting](#monitoring--troubleshooting)
13. [AI Usage Disclosure](#ai-usage-disclosure)

## Project Overview

The Rearc Data Quest is a comprehensive data engineering project that demonstrates:

- **Data Management**: Sourcing and synchronizing datasets from external sources (BLS)
- **API Integration**: Fetching and processing data from public APIs (DataUSA)
- **Data Analytics**: Generating insights and reports from combined datasets
- **Infrastructure as Code**: Automating deployment with Terraform
- **AWS Services**: Lambda, S3, SQS, EventBridge, CloudWatch

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     EventBridge Rule                        │
│                  (Daily at 2 AM UTC)                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────┐
        │  Combined Lambda Function      │
        │  (Part 1 & 2 Data Pipeline)    │
        └────┬───────────────────────┬───┘
             │                       │
             ▼                       ▼
    ┌─────────────────┐    ┌──────────────────┐
    │  BLS Sync       │    │  Population API  │
    │  (Part 1)       │    │  (Part 2)        │
    └────────┬────────┘    └────────┬─────────┘
             │                      │
             └──────────┬───────────┘
                        ▼
                  ┌──────────────┐
                  │  S3 Bucket   │
                  │  (Raw Data)  │
                  └──────┬───────┘
                         │
          ┌──────────────┴──────────────┐
          │ S3 Event Notification       │
          └──────────────┬──────────────┘
                         ▼
                  ┌──────────────┐
                  │  SQS Queue   │
                  └──────┬───────┘
                         │
                         ▼
          ┌──────────────────────────┐
          │  Analytics Lambda        │
          │  (Part 3 Reports)        │
          │  - Report 1: Pop Stats   │
          │  - Report 2: Best Year   │
          │  - Report 3: Combined    │
          └──────────────────────────┘
```

## Prerequisites

### Local Development

- Python 3.11+
- AWS Account with appropriate permissions
- AWS CLI v2 configured with credentials
- Terraform 1.0+
- Git
- Bash/PowerShell

### AWS Permissions Required

Your IAM user/role needs permissions for:

- S3: Create buckets, upload/download objects, manage versioning
- Lambda: Create functions, manage layers, invoke functions
- SQS: Create queues, manage policies
- EventBridge: Create rules and targets
- CloudWatch: Create log groups, alarms
- IAM: Create roles and policies

### Installing Prerequisites

#### AWS CLI
```bash
# Windows (using chocolatey)
choco install awscli

# macOS
brew install awscli

# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

#### Terraform
```bash
# Windows (using chocolatey)
choco install terraform

# macOS
brew install terraform

# Linux
wget https://releases.hashicorp.com/terraform/1.5.0/terraform_1.5.0_linux_amd64.zip
unzip terraform_1.5.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/
```

#### Python Dependencies
```bash
pip install -r requirements.txt
```

## Project Structure

```
quest_submit/
├── part_1_s3_sync/
│   └── sync_bls_data.py          # BLS data synchronization
├── part_2_api/
│   └── fetch_population_data.py  # Population API integration
├── part_3_analytics/
│   └── analytics.py               # Data analytics and reporting
├── part_4_terraform/
│   ├── main.tf                   # Main infrastructure configuration
│   ├── variables.tf              # Variable definitions
│   ├── outputs.tf                # Output definitions
│   └── terraform.tfvars.example  # Example variables file
├── lambda_functions/
│   ├── combined_lambda.py        # Part 1 & 2 combined Lambda
│   └── analytics_lambda.py       # Part 3 analytics Lambda
├── requirements.txt              # Python dependencies
├── build.sh                      # Build script for Lambda packages
├── deploy.sh                     # Deployment script
├── .gitignore                    # Git ignore rules
└── README.md                     # This file
```

## Setup Instructions

### 1. Clone and Configure

```bash
# Clone the repository
git clone <repository-url>
cd quest_submit

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure AWS Credentials

```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter default region (e.g., us-east-1)
# Enter default output format (json)
```

### 3. Update Contact Information

Update the `User-Agent` header in the Python scripts to comply with BLS policies:

**part_1_s3_sync/sync_bls_data.py** (line ~24)
```python
HEADERS = {
    "User-Agent": "your.email@example.com"  # Replace with your email
}
```

**part_2_api/fetch_population_data.py** (line ~24)
```python
HEADERS = {
    "User-Agent": "your.email@example.com"  # Replace with your email
}
```

### 4. Prepare Terraform Configuration

```bash
cd part_4_terraform

# Copy example variables file
cp terraform.tfvars.example terraform.tfvars

# Edit terraform.tfvars with your settings
# nano terraform.tfvars  # or use your preferred editor
```

Example `terraform.tfvars`:
```hcl
aws_region     = "us-east-1"
environment    = "dev"
s3_bucket_name = "rearc-quest-data"
lambda_timeout = 300
lambda_memory  = 512

tags = {
  Project     = "rearc-quest"
  Environment = "dev"
  Owner       = "YourName"
}
```

## Deployment

### Option 1: Automated Deployment (Recommended)

```bash
# From project root
chmod +x deploy.sh build.sh
./build.sh      # Build Lambda packages
./deploy.sh     # Deploy infrastructure

# When prompted, review the Terraform plan and type 'yes' to confirm
```

### Option 2: Manual Deployment

```bash
# Build Lambda packages
./build.sh

# Navigate to Terraform directory
cd part_4_terraform

# Initialize Terraform
terraform init

# Review plan
terraform plan

# Apply configuration
terraform apply

# View outputs
terraform output
```

### Option 3: Local Testing (Without Deployment)

```bash
# Test Part 1: BLS Sync
python part_1_s3_sync/sync_bls_data.py

# Test Part 2: Population API
python part_2_api/fetch_population_data.py

# Test Part 3: Analytics
python part_3_analytics/analytics.py data/pr.data.0.Current data/population.json
```

## Part 1: BLS Data Sync

### Overview

Syncs the Bureau of Labor Statistics time series data to S3 while maintaining consistency with the source.

**Key Features:**
- Fetches file list from BLS server
- Compares file hashes to avoid unnecessary uploads
- Deletes files from S3 that are no longer on BLS
- Handles BLS access policies via User-Agent header
- Scheduled daily execution

### Implementation Details

**File:** `part_1_s3_sync/sync_bls_data.py`

**Class:** `BLSDataSync`

**Methods:**
- `get_remote_file_list()` - Fetch list of files from BLS
- `get_file_hash()` - Compute MD5 hash of remote file
- `get_s3_file_hash()` - Retrieve hash of S3 file
- `upload_file_to_s3()` - Download and upload file to S3
- `delete_removed_files()` - Clean up deleted files
- `sync()` - Execute full sync operation

**Lambda Handler:**
```python
def lambda_handler(event, context):
    # Triggered daily by EventBridge
    syncer = BLSDataSync(S3_BUCKET)
    success = syncer.sync()
    return {'statusCode': 200 if success else 500, 'body': ...}
```

### Testing

```bash
# Test locally
python part_1_s3_sync/sync_bls_data.py

# Monitor logs
aws logs tail /aws/lambda/rearc-quest-combined-data-pipeline --follow
```

## Part 2: Population API

### Overview

Fetches US population data from DataUSA API and stores as JSON in S3.

**Key Features:**
- Calls DataUSA population endpoint
- Extracts yearly population data
- Adds metadata (fetch time, API URL, parameters)
- Stores in S3 for downstream processing
- S3 event triggers analytics pipeline

### Implementation Details

**File:** `part_2_api/fetch_population_data.py`

**Class:** `PopulationDataFetcher`

**Methods:**
- `fetch_population_data()` - Call DataUSA API
- `save_to_s3()` - Store JSON data in S3
- `fetch_and_save()` - Combined operation

**Lambda Handler:**
```python
def lambda_handler(event, context):
    # Triggered daily via EventBridge (Part of combined Lambda)
    fetcher = PopulationDataFetcher(S3_BUCKET)
    success = fetcher.fetch_and_save()
    return {'statusCode': 200 if success else 500, 'body': ...}
```

### Testing

```bash
# Test API fetch locally
python part_2_api/fetch_population_data.py

# Verify S3 upload
aws s3 ls s3://rearc-quest-data-[ACCOUNT-ID]/population_data/
```

## Part 3: Data Analytics

### Overview

Generates three analytical reports from BLS and population data.

**Reports:**

1. **Report 1: Population Statistics (2013-2018)**
   - Mean US population
   - Standard deviation
   - Years covered: 2013-2018

2. **Report 2: Best Year per Series**
   - For each series_id in BLS data
   - Find year with maximum quarterly value sum
   - Output: series_id, best_year, summed_value

3. **Report 3: Combined Analysis**
   - Filter for series_id: PRS30006032, period: Q01
   - Join with population data by year
   - Output: series_id, year, period, value, population

### Implementation Details

**File:** `part_3_analytics/analytics.py`

**Class:** `DataAnalytics`

**Methods:**
- `load_bls_csv()` - Load BLS CSV data
- `load_population_json()` - Load population JSON
- `load_bls_from_s3()` - Load BLS from S3
- `load_population_from_s3()` - Load population from S3
- `report_1_population_stats()` - Generate Report 1
- `report_2_best_year_per_series()` - Generate Report 2
- `report_3_combined_analysis()` - Generate Report 3

### Testing

```bash
# Test analytics locally
python part_3_analytics/analytics.py data/pr.data.0.Current data/population_data.json ./reports

# Results saved to: reports/report_2_best_year.csv, reports/report_3_combined.csv
```

### Lambda Handler

```python
def lambda_handler(event, context):
    # Triggered by S3 -> SQS -> Lambda
    # Generates reports and logs results
    results = generate_reports_from_s3()
    logger.info(f"Report 1: {results['report_1']}")
    logger.info(f"Report 2: {len(results['report_2'])} rows")
    logger.info(f"Report 3: {len(results['report_3'])} rows")
    return {'statusCode': 200, 'body': json.dumps(results)}
```

## Part 4: Infrastructure & Automation

### Overview

Complete AWS infrastructure deployed with Terraform to automate the entire pipeline.

### Resources Created

#### Compute
- **Combined Lambda Function** - Runs Part 1 & 2 daily
- **Analytics Lambda Function** - Processes analytics on demand
- **Lambda Layer** - Shared Python dependencies

#### Storage
- **S3 Bucket** - Stores all data
  - Versioning enabled
  - Public access blocked
  - Event notifications configured

#### Messaging
- **SQS Queue** - Processes analytics jobs
- **Queue Policy** - Allows S3 to send messages

#### Scheduling
- **EventBridge Rule** - Triggers daily at 2 AM UTC
- **EventBridge Target** - Routes to combined Lambda

#### Monitoring
- **CloudWatch Log Groups** - Capture Lambda logs
- **CloudWatch Alarms** - Alert on Lambda errors

#### IAM
- **Lambda Execution Role** - S3, SQS, CloudWatch permissions
- **Role Policy** - Least privilege access

### Terraform Configuration

**Main Configuration:** `part_4_terraform/main.tf`

**Key Resources:**
- `aws_s3_bucket` - Data storage
- `aws_lambda_function` - Serverless compute
- `aws_sqs_queue` - Message queue
- `aws_cloudwatch_event_rule` - Scheduler
- `aws_iam_role` - Execution permissions

**Variables:** `part_4_terraform/variables.tf`

**Outputs:** `part_4_terraform/outputs.tf`

### Deployment

See [Deployment](#deployment) section above.

### Monitoring

```bash
# View Lambda execution logs
aws logs tail /aws/lambda/rearc-quest-combined-data-pipeline --follow

# View SQS queue depth
aws sqs get-queue-attributes \
  --queue-url <QUEUE_URL> \
  --attribute-names ApproximateNumberOfMessages

# Check EventBridge rule
aws events describe-rule --name rearc-quest-daily-schedule

# View alarms
aws cloudwatch describe-alarms --alarm-names rearc-quest-combined-lambda-errors
```

## Testing & Validation

### 1. Test BLS Sync Locally

```bash
# Set AWS credentials
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1

# Run sync
python part_1_s3_sync/sync_bls_data.py

# Check results
aws s3 ls s3://rearc-quest-data-[ACCOUNT-ID]/bls_time_series/ --recursive
```

### 2. Test Population API Locally

```bash
python part_2_api/fetch_population_data.py

# Verify S3 upload
aws s3 cp s3://rearc-quest-data-[ACCOUNT-ID]/population_data/population_data.json - | head -20
```

### 3. Test Analytics Locally

Download sample data:
```bash
# Download BLS sample file
wget https://download.bls.gov/pub/time.series/pr/pr.data.0.Current -O data/pr.data.0.Current

# Create sample population data
cat > data/population.json << 'EOF'
{
  "data": [
    {"Year": 2013, "Population": 315005716},
    {"Year": 2014, "Population": 317297725},
    {"Year": 2015, "Population": 319297384},
    {"Year": 2016, "Population": 322999999},
    {"Year": 2017, "Population": 325084756},
    {"Year": 2018, "Population": 327167439}
  ]
}
EOF

python part_3_analytics/analytics.py data/pr.data.0.Current data/population.json data/
```

### 4. Test Lambda Functions

#### Deploy and Test Combined Lambda

```bash
# After deploying with Terraform
aws lambda invoke \
  --function-name rearc-quest-combined-data-pipeline \
  response.json

cat response.json
```

#### View Lambda Logs

```bash
# Combined Lambda
aws logs tail /aws/lambda/rearc-quest-combined-data-pipeline --since 1h

# Analytics Lambda
aws logs tail /aws/lambda/rearc-quest-analytics --since 1h
```

### 5. Test End-to-End Pipeline

```bash
# Trigger combined Lambda
aws lambda invoke \
  --function-name rearc-quest-combined-data-pipeline \
  --cli-binary-format raw-in-base64-out \
  response.json

# Wait for S3 event to trigger analytics
sleep 10

# Check analytics Lambda logs
aws logs tail /aws/lambda/rearc-quest-analytics --since 1m
```

## Monitoring & Troubleshooting

### CloudWatch Dashboards

Create a custom dashboard to monitor your pipeline:

```bash
# View available metrics
aws cloudwatch list-metrics --namespace AWS/Lambda

# Create alarm for Lambda errors
aws cloudwatch put-metric-alarm \
  --alarm-name rearc-quest-lambda-errors \
  --alarm-description "Alert on Lambda errors" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --threshold 1 \
  --comparison-operator GreaterThanOrEqualToThreshold
```

### Common Issues

#### 1. BLS 403 Forbidden Error

**Cause:** Missing User-Agent header

**Solution:** Update `HEADERS` in both Python scripts with your email

#### 2. Lambda Timeout

**Cause:** Processing takes longer than timeout

**Solution:** Increase timeout in `variables.tf` or optimize code

#### 3. S3 Access Denied

**Cause:** IAM permissions missing

**Solution:** Verify Lambda role has S3 permissions

#### 4. SQS Messages Not Processing

**Cause:** Lambda not subscribed or S3 event notification misconfigured

**Solution:** Verify S3 bucket notification configuration

```bash
aws s3api get-bucket-notification-configuration \
  --bucket rearc-quest-data-[ACCOUNT-ID]
```

#### 5. API Rate Limiting

**Cause:** Too many requests to DataUSA

**Solution:** Implement exponential backoff (already in code)

### Debugging

Enable debug logging:

```python
# In Python scripts, change logging level
logging.basicConfig(level=logging.DEBUG)

# Or set environment variable
export LOG_LEVEL=DEBUG
```

Check detailed Lambda logs:

```bash
aws lambda get-function --function-name rearc-quest-combined-data-pipeline
aws lambda get-function-concurrency --function-name rearc-quest-combined-data-pipeline
```

## Cost Estimation

### Monthly Costs (Approximate)

| Service | Usage | Cost |
|---------|-------|------|
| Lambda | 2x daily invocations + analytics | $0.20 |
| S3 | Storage (100 GB) + requests | $2.50 |
| CloudWatch | Logs + alarms | $1.00 |
| SQS | Messages | $0.20 |
| **Total** | | **~$4.00/month** |

### Cost Optimization

- Use S3 lifecycle policies for old data
- Set Lambda memory appropriately
- Batch SQS messages
- Archive old logs

## Cleanup

To remove all AWS resources:

```bash
cd part_4_terraform

# Remove all resources
terraform destroy

# Confirm by typing 'yes'
```

## Next Steps

### Enhancements

1. **Add Data Validation** - Validate data quality before uploading
2. **Implement Retries** - Handle transient failures
3. **Add Notifications** - Send alerts on pipeline completion
4. **Create Athena Tables** - Query data with SQL
5. **Add QuickSight Dashboards** - Visualize results
6. **Implement Dead Letter Queue** - Handle failed messages

### Production Deployment

1. **Set up Terraform backend** - Use S3 + DynamoDB for state
2. **Configure CI/CD** - Use CodePipeline for deployments
3. **Add VPC** - Run Lambda in VPC for security
4. **Enable encryption** - KMS for S3 and SQS
5. **Implement cost controls** - Set AWS budgets and alerts

## AI Usage Disclosure

This implementation was assisted by AI tools:

**What AI was used for:**
- Code structure and architecture design
- Lambda function templates
- Terraform configuration patterns
- Error handling and best practices
- Documentation generation

**What was manually verified:**
- All code logic and correctness
- AWS permissions and IAM policies
- Integration between components
- Testing and validation procedures
- Contact information and headers

**Improvements made beyond initial generation:**
- Added comprehensive error handling
- Implemented proper logging throughout
- Added data validation and sanitization
- Optimized resource usage
- Enhanced security with least privilege access

## Support & Documentation

- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [DataUSA API Documentation](https://datausa.io/about/api/)
- [BLS Data Access Policy](https://www.bls.gov/bls/pss.htm)
- [Pandas Documentation](https://pandas.pydata.org/docs/)

## License

This project is provided as-is for the Rearc Data Quest assignment.

## Contact

For questions or issues, please refer to the comments in each file or contact your assignment reviewer.
