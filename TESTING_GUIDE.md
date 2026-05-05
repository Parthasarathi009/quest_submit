# How to Run and Test the Rearc Quest Implementation

## 🧪 Testing Guide - Complete Instructions

### Prerequisites Check

First, verify your setup is correct:

```powershell
# PowerShell (Windows)
python validate.py

# Or Linux/macOS
python3 validate.py
```

This will check:
- ✅ All files exist
- ✅ Python version (3.11+)
- ✅ Required packages installed
- ✅ AWS credentials configured
- ✅ Terraform installed
- ✅ Contact info updated (BLS compliance)

---

## Part 1: Test BLS Data Sync Locally

### Quick Test (5 minutes)

```powershell
# Windows PowerShell
python part_1_s3_sync/sync_bls_data.py

# Linux/macOS
python3 part_1_s3_sync/sync_bls_data.py
```

**Expected Output:**
```
2026-05-05 10:30:45 - INFO - Starting BLS data sync...
2026-05-05 10:30:45 - INFO - Fetching data from https://download.bls.gov/pub/time.series/pr/
2026-05-05 10:30:47 - INFO - Found 45 files on BLS server
2026-05-05 10:30:48 - INFO - Successfully uploaded pr.data.0.Current to S3
...
```

**What it does:**
- Connects to AWS S3
- Creates bucket (if doesn't exist)
- Downloads sample files from BLS
- Uploads to S3

### Troubleshooting Part 1 Test

**Error: "403 Forbidden"**
→ Update email in `part_1_s3_sync/sync_bls_data.py` line 24

**Error: "NoCredentialsError"**
→ Run `aws configure` first

**Error: "ImportError: No module named boto3"**
→ Run `pip install -r requirements.txt`

---

## Part 2: Test Population API Locally

### Quick Test (2 minutes)

```powershell
python part_2_api/fetch_population_data.py
```

**Expected Output:**
```
2026-05-05 10:30:45 - INFO - Fetching data from API: https://honolulu-api.datausa.io/tesseract/data.jsonrecords
2026-05-05 10:30:46 - INFO - Successfully fetched data. Records: 8
2026-05-05 10:30:47 - INFO - Successfully saved data to s3://rearc-quest-data-123456789/population_data/population_data.json
```

**What it does:**
- Calls DataUSA Population API
- Gets yearly US population data
- Saves as JSON to S3

### Verify Results in S3

```powershell
# List population data files
aws s3 ls s3://rearc-quest-data-123456789/population_data/

# Download and view the data
aws s3 cp s3://rearc-quest-data-123456789/population_data/population_data.json -

# Or save to file
aws s3 cp s3://rearc-quest-data-123456789/population_data/population_data.json population_data.json
type population_data.json  # View file
```

---

## Part 3: Test Analytics Locally

### Step 1: Download Sample Data

```powershell
# Create data directory
mkdir data -Force

# Download BLS sample file (this may take a minute)
$url = "https://download.bls.gov/pub/time.series/pr/pr.data.0.Current"
$output = "data/pr.data.0.Current"
Invoke-WebRequest -Uri $url -OutFile $output -UserAgent "your.email@example.com"

# Create sample population data
$populationJson = @{
    data = @(
        @{Year = 2013; Population = 315005716},
        @{Year = 2014; Population = 317297725},
        @{Year = 2015; Population = 319297384},
        @{Year = 2016; Population = 322999999},
        @{Year = 2017; Population = 325084756},
        @{Year = 2018; Population = 327167439}
    )
} | ConvertTo-Json

$populationJson | Out-File -FilePath "data/population_data.json"
```

### Step 2: Run Analytics

```powershell
# Create output directory
mkdir reports -Force

# Run analytics
python part_3_analytics/analytics.py data/pr.data.0.Current data/population_data.json reports/
```

**Expected Output:**
```
2026-05-05 10:30:45 - INFO - Loading BLS data from data/pr.data.0.Current
2026-05-05 10:30:46 - INFO - Loaded BLS data with shape: (12345, 5)
2026-05-05 10:30:46 - INFO - Loading population data from data/population_data.json
2026-05-05 10:30:46 - INFO - Loaded population data with shape: (6, 2)
2026-05-05 10:30:46 - INFO - Generating Report 1: Population Statistics (2013-2018)
2026-05-05 10:30:46 - INFO - Report 1 complete: Mean=320923053.17, StdDev=5071423.51
2026-05-05 10:30:47 - INFO - Generating Report 2: Best Year per Series ID
2026-05-05 10:30:47 - INFO - Report 2 complete: 89 series found
2026-05-05 10:30:48 - INFO - Generating Report 3: Combined BLS and Population Analysis
2026-05-05 10:30:48 - INFO - Report 3 complete: 6 records found
2026-05-05 10:30:48 - INFO - All reports generated successfully
```

### Step 3: Check Results

```powershell
# View Report 2 results
type reports/report_2_best_year.csv | Select-Object -First 10

# View Report 3 results
type reports/report_3_combined.csv | Select-Object -First 10
```

**Report 2 Output:**
```csv
series_id,year,value
PRS30006011,1996,7
PRS30006012,2000,8
PRS30006021,2000,15
...
```

**Report 3 Output:**
```csv
series_id,year,period,value,Population
PRS30006032,2013,Q01,1.9,315005716
PRS30006032,2014,Q01,2.0,317297725
...
```

---

## Unit Tests: Test Everything Automatically

### Run All Tests

```powershell
# Install test dependencies
pip install pytest pytest-cov moto

# Run tests
pytest tests/ -v --cov=. --cov-report=term-missing
```

**Expected Output:**
```
tests/test_part1.py::TestBLSDataSync::test_get_remote_file_list PASSED
tests/test_part1.py::TestBLSDataSync::test_get_file_hash PASSED
tests/test_part1.py::TestBLSDataSync::test_upload_file_to_s3 PASSED
tests/test_part2.py::TestPopulationDataFetcher::test_fetch_population_data PASSED
tests/test_part2.py::TestPopulationDataFetcher::test_save_to_s3 PASSED
tests/test_part3.py::TestDataAnalytics::test_report_1_population_stats PASSED
tests/test_part3.py::TestDataAnalytics::test_report_2_best_year_per_series PASSED
tests/test_part3.py::TestDataAnalytics::test_report_3_combined_analysis PASSED

======================== 8 passed in 2.15s =========================
```

### Run Specific Tests

```powershell
# Test only Part 1
pytest tests/test_part1.py -v

# Test only Part 3
pytest tests/test_part3.py -v

# Run single test
pytest tests/test_part1.py::TestBLSDataSync::test_get_file_hash -v
```

---

## 🚀 Deploy to AWS - Full Pipeline Test

### Step 1: Prepare for Deployment

```powershell
# Verify everything is set up
python validate.py

# Should show: "All validations passed! Ready to deploy."
```

### Step 2: Build Lambda Packages

```powershell
# Option A: Windows PowerShell
.\build.ps1

# Option B: Linux/macOS
bash build.sh
```

**Expected files created:**
```
✓ combined_lambda.zip      (Part 1 & 2)
✓ analytics_lambda.zip     (Part 3)
✓ python_dependencies.zip  (Shared libraries)
```

### Step 3: Deploy Infrastructure

```powershell
# Option A: Fully Automated (Recommended)
bash deploy.sh

# When prompted: type 'yes' to apply

# Option B: Manual Terraform Steps
cd part_4_terraform
terraform init
terraform plan
terraform apply
cd ..
```

**What gets created:**
```
✓ S3 bucket
✓ Lambda functions
✓ SQS queue
✓ EventBridge rule (daily scheduler)
✓ CloudWatch log groups
✓ IAM roles and policies
✓ Alarms
```

### Step 3b: Save Deployment Info

```powershell
cd part_4_terraform
terraform output > ..\deployment_info.txt
cd ..

type deployment_info.txt
```

**Output shows:**
```
s3_bucket_name = "rearc-quest-data-123456789"
combined_lambda_function_name = "rearc-quest-combined-data-pipeline"
analytics_lambda_function_name = "rearc-quest-analytics"
sqs_queue_url = "https://sqs.us-east-1.amazonaws.com/123456789/rearc-quest-analytics-queue"
```

---

## ✅ Verify Deployment

### Check AWS Resources

```powershell
# List S3 buckets
aws s3 ls | findstr rearc-quest

# List Lambda functions
aws lambda list-functions | findstr rearc-quest

# Check SQS queues
aws sqs list-queues | findstr rearc-quest

# Check EventBridge rules
aws events list-rules --name-prefix rearc-quest

# Check CloudWatch log groups
aws logs describe-log-groups | findstr rearc-quest
```

### View Bucket Contents

```powershell
# See all objects in bucket
aws s3 ls s3://rearc-quest-data-123456789/ --recursive

# View BLS files
aws s3 ls s3://rearc-quest-data-123456789/bls_time_series/ --recursive | head -20

# View population data
aws s3 ls s3://rearc-quest-data-123456789/population_data/
```

---

## 🧪 Manual Testing - Trigger Lambda Functions

### Test Combined Lambda (Part 1 & 2)

```powershell
# Invoke the lambda
aws lambda invoke `
  --function-name rearc-quest-combined-data-pipeline `
  response.json

# View the response
type response.json
```

**Expected Response:**
```json
{
  "statusCode": 200,
  "body": {
    "timestamp": "2026-05-05T10:30:45.123456",
    "part_1_bls_sync": {
      "success": true,
      "status": "Completed"
    },
    "part_2_population_api": {
      "success": true,
      "status": "Completed"
    }
  }
}
```

### Monitor Lambda Logs

```powershell
# View combined lambda logs (last 1 hour)
aws logs tail /aws/lambda/rearc-quest-combined-data-pipeline --since 1h

# Follow logs in real-time
aws logs tail /aws/lambda/rearc-quest-combined-data-pipeline --follow

# View analytics lambda logs
aws logs tail /aws/lambda/rearc-quest-analytics --follow

# Get specific log stream
aws logs describe-log-streams --log-group-name /aws/lambda/rearc-quest-combined-data-pipeline
```

### Test SQS Queue

```powershell
# Get queue attributes (message count)
$queueUrl = "https://sqs.us-east-1.amazonaws.com/123456789/rearc-quest-analytics-queue"

aws sqs get-queue-attributes `
  --queue-url $queueUrl `
  --attribute-names ApproximateNumberOfMessages

# Receive messages
aws sqs receive-message --queue-url $queueUrl

# Get queue URL programmatically
aws sqs get-queue-url --queue-name rearc-quest-analytics-queue
```

### Test Analytics Lambda (Manual)

```powershell
# Create a test SQS message
$testEvent = @{
    Records = @(
        @{
            messageId = "test-message-1"
            body = "Test message"
        }
    )
} | ConvertTo-Json

# Save to file
$testEvent | Out-File test-event.json

# Invoke analytics lambda
aws lambda invoke `
  --function-name rearc-quest-analytics `
  --payload file://test-event.json `
  response.json

# View response
type response.json
```

---

## 📊 End-to-End Test Sequence

Run these steps in order to test the complete pipeline:

```powershell
# Step 1: Validate setup
Write-Host "Step 1: Validating setup..."
python validate.py

# Step 2: Test BLS Sync locally
Write-Host "Step 2: Testing BLS Sync..."
python part_1_s3_sync/sync_bls_data.py

# Step 3: Test Population API locally
Write-Host "Step 3: Testing Population API..."
python part_2_api/fetch_population_data.py

# Step 4: Test Analytics locally
Write-Host "Step 4: Testing Analytics..."
mkdir data -Force
mkdir reports -Force
# (Download data files as shown above)
python part_3_analytics/analytics.py data/pr.data.0.Current data/population_data.json reports/

# Step 5: Run unit tests
Write-Host "Step 5: Running unit tests..."
pytest tests/ -v

# Step 6: Build Lambda packages
Write-Host "Step 6: Building Lambda packages..."
.\build.ps1

# Step 7: Deploy to AWS
Write-Host "Step 7: Deploying to AWS..."
bash deploy.sh

# Step 8: Verify deployment
Write-Host "Step 8: Verifying deployment..."
aws lambda list-functions | findstr rearc-quest
aws s3 ls | findstr rearc-quest

# Step 9: Trigger combined lambda
Write-Host "Step 9: Testing combined lambda..."
aws lambda invoke `
  --function-name rearc-quest-combined-data-pipeline `
  response.json
type response.json

# Step 10: Check logs
Write-Host "Step 10: Checking logs..."
aws logs tail /aws/lambda/rearc-quest-combined-data-pipeline --since 5m
```

---

## 🔍 Troubleshooting Tests

### Local Script Fails

**"Module not found" error**
```powershell
pip install -r requirements.txt
```

**"AWS credentials not configured"**
```powershell
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter region: us-east-1
# Enter output format: json
```

**"403 Forbidden from BLS"**
```
Update email in:
- part_1_s3_sync/sync_bls_data.py (line 24)
- part_2_api/fetch_population_data.py (line 24)
```

### Lambda Deployment Fails

**"Terraform not initialized"**
```powershell
cd part_4_terraform
terraform init
cd ..
```

**"Lambda timeout"**
Increase in `part_4_terraform/terraform.tfvars`:
```hcl
lambda_timeout = 600  # Instead of 300
```

### Lambda Invocation Fails

**"Function not found"**
```powershell
# Check function exists
aws lambda list-functions --query 'Functions[*].FunctionName'
```

**"No permissions"**
Check IAM role has S3 and logs permissions

---

## 📈 Check Costs

```powershell
# Get cost estimate for current month
aws ce get-cost-and-usage `
  --time-period Start=2026-05-01,End=2026-05-31 `
  --granularity MONTHLY `
  --metrics "BlendedCost" `
  --group-by Type=DIMENSION,Key=SERVICE
```

---

## 🧹 Cleanup - Remove Everything

When done testing:

```powershell
# Delete all AWS resources
cd part_4_terraform
terraform destroy
# Type 'yes' to confirm

cd ..

# Delete local build files
Remove-Item -Recurse -Force build/
Remove-Item -Force *.zip
Remove-Item -Recurse -Force data/
Remove-Item -Recurse -Force reports/
```

---

## 📋 Quick Test Checklist

- [ ] Run `python validate.py` - All pass?
- [ ] Run `python part_1_s3_sync/sync_bls_data.py` - Success?
- [ ] Run `python part_2_api/fetch_population_data.py` - Success?
- [ ] Run `python part_3_analytics/analytics.py ...` - Reports generated?
- [ ] Run `pytest tests/ -v` - All tests pass?
- [ ] Run `.\build.ps1` - Packages created?
- [ ] Run `bash deploy.sh` - Infrastructure deployed?
- [ ] Run `aws lambda invoke ...` - Lambda works?
- [ ] Check `aws logs tail ...` - Logs appear?

---

## 🚀 You're Ready!

Once all tests pass, you're ready to:
1. ✅ Submit your code
2. ✅ Show AWS resources in console
3. ✅ Demonstrate daily automation
4. ✅ Explain the pipeline architecture
