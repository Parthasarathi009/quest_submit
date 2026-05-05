# Quick Start Guide

## 5-Minute Setup

### 1. Configure AWS (2 min)

```bash
# Install AWS CLI if you haven't already
# https://aws.amazon.com/cli/

# Configure credentials
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter default region: us-east-1
# Enter output format: json

# Verify configuration
aws sts get-caller-identity
```

### 2. Update Contact Info (1 min)

Edit two files to add your email for BLS compliance:

**part_1_s3_sync/sync_bls_data.py** (around line 24)
```python
HEADERS = {
    "User-Agent": "your.email@example.com"  # Change this
}
```

**part_2_api/fetch_population_data.py** (around line 24)
```python
HEADERS = {
    "User-Agent": "your.email@example.com"  # Change this
}
```

### 3. Test Locally (2 min)

```bash
# Install dependencies
pip install -r requirements.txt

# Test Part 1 - BLS Sync (reads BLS data)
python part_1_s3_sync/sync_bls_data.py

# Test Part 2 - Population API (reads population data)
python part_2_api/fetch_population_data.py

# All tests passed? Ready to deploy!
```

## Deploy to AWS

### Option A: Fully Automated (Recommended)

```bash
# Everything runs in one command
bash deploy.sh

# Answer 'yes' when prompted to apply changes
```

### Option B: Manual Steps

```bash
# Step 1: Build Lambda packages
bash build.sh
# Creates: combined_lambda.zip, analytics_lambda.zip, python_dependencies.zip

# Step 2: Configure Terraform
cd part_4_terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your settings

# Step 3: Deploy
terraform init
terraform plan
terraform apply
# Review the plan and type 'yes'

# Step 4: Save outputs
terraform output > deployment_info.txt
```

## Verify Deployment

```bash
# Check S3 bucket created
aws s3 ls | grep rearc-quest-data

# Check Lambda functions
aws lambda list-functions | grep rearc-quest

# Check SQS queue
aws sqs list-queues | grep rearc-quest

# Check EventBridge rule
aws events describe-rule --name rearc-quest-daily-schedule

# View Lambda logs
aws logs tail /aws/lambda/rearc-quest-combined-data-pipeline --follow
```

## Manual Testing

### Trigger Combined Lambda (Part 1 & 2)

```bash
aws lambda invoke \
  --function-name rearc-quest-combined-data-pipeline \
  response.json

cat response.json
```

### View Results

```bash
# Check what was uploaded to S3
aws s3 ls s3://rearc-quest-data-[ACCOUNT-ID]/ --recursive

# Download and inspect population data
aws s3 cp s3://rearc-quest-data-[ACCOUNT-ID]/population_data/population_data.json - | head -20

# Download and inspect BLS data
aws s3 cp s3://rearc-quest-data-[ACCOUNT-ID]/bls_time_series/pr.data.0.Current - | head -10
```

### Check Analytics Logs

```bash
# View analytics Lambda logs
aws logs tail /aws/lambda/rearc-quest-analytics --follow

# View CloudWatch alarms
aws cloudwatch describe-alarms --alarm-names rearc-quest-combined-lambda-errors
```

## Common Operations

### List Project Files

```bash
tree -L 2  # Linux/macOS
# or
Get-ChildItem -Recurse -Depth 2  # Windows PowerShell
```

### Run All Tests

```bash
pip install pytest pytest-cov
pytest tests/ -v --cov
```

### Check Costs

```bash
# Estimate monthly cost
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics "UnblendedCost"
```

### Cleanup

```bash
# Remove all AWS resources
cd part_4_terraform
terraform destroy
# Type 'yes' to confirm

# Remove local build artifacts
rm -rf build/ *.zip

# Remove Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
```

## Troubleshooting

### BLS 403 Error?
→ Update User-Agent header with your email

### Lambda Timeout?
→ Increase `lambda_timeout` in `terraform.tfvars`

### S3 Access Denied?
→ Check AWS credentials with `aws sts get-caller-identity`

### Need Help?
→ Check logs with `aws logs tail /aws/lambda/...`
→ Read IMPLEMENTATION_GUIDE.md for detailed docs

## What Happens Daily

1. **2:00 AM UTC** - EventBridge triggers combined Lambda
2. **Combined Lambda runs:**
   - Part 1: Syncs BLS data to S3
   - Part 2: Fetches population API, saves to S3
3. **S3 Event Triggered:** Population data upload notifies SQS
4. **Analytics Lambda Runs:** Processes analytics on SQS message
5. **Reports Generated:** Logged to CloudWatch

## Next Steps

1. ✅ Update contact info (BLS compliance)
2. ✅ Test locally
3. ✅ Deploy to AWS
4. ✅ Verify in AWS Console
5. ✅ Monitor logs
6. 🔄 Check data in S3 (tomorrow at 2 AM UTC)

## Quick Commands Reference

```bash
# Setup
pip install -r requirements.txt

# Test
python part_1_s3_sync/sync_bls_data.py
python part_2_api/fetch_population_data.py

# Build & Deploy
./build.sh && ./deploy.sh

# Monitor
aws logs tail /aws/lambda/rearc-quest-combined-data-pipeline --follow
aws logs tail /aws/lambda/rearc-quest-analytics --follow

# Cleanup
terraform destroy
```

---

**Questions?** See IMPLEMENTATION_GUIDE.md for comprehensive documentation.
