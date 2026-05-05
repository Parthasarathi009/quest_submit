# Step-by-Step: Complete Testing & Deployment Walkthrough

Follow these exact steps in order. Don't skip any!

---

## 🚀 STEP 1: Initial Setup (5 minutes)

### 1.1 Open PowerShell Terminal

```
In VS Code:
- Press Ctrl + `  (backtick)
- Or: View → Terminal
```

### 1.2 Navigate to Project

```powershell
cd "C:\Users\sssuv\OneDrive - Bridgewater State University\Documents\Git\Parth\quest_submit"

# Verify you're in right location
pwd
# Should show: quest_submit
```

### 1.3 Install Python Dependencies

```powershell
pip install -r requirements.txt
```

**Watch for:**
- ✅ Successfully installed boto3
- ✅ Successfully installed requests
- ✅ Successfully installed pandas
- ✅ Successfully installed pytest

**If error:** Run `python -m pip install --upgrade pip` first

### 1.4 Update Email Addresses (BLS Compliance)

**File 1:** `part_1_s3_sync/sync_bls_data.py`
- Open the file
- Find line 24
- Replace `"contact@yourcompany.com"` with `"your.email@example.com"`
- Save

**File 2:** `part_2_api/fetch_population_data.py`
- Open the file
- Find line 24
- Replace `"contact@yourcompany.com"` with `"your.email@example.com"`
- Save

### 1.5 Configure AWS Credentials

```powershell
aws configure
```

When prompted, enter:
```
AWS Access Key ID: [your-access-key]
AWS Secret Access Key: [your-secret-key]
Default region name: us-east-1
Default output format: json
```

**Verify it worked:**
```powershell
aws sts get-caller-identity
```

Should show your AWS account info.

---

## ✅ STEP 2: Validate Everything (2 minutes)

```powershell
python validate.py
```

**Expected Output:**
```
============================================================
         Rearc Data Quest - Setup Validation
============================================================

Validating Project Structure
✓ Part 1: BLS Sync: part_1_s3_sync/sync_bls_data.py
✓ Part 2: Population API: part_2_api/fetch_population_data.py
✓ Part 3: Analytics: part_3_analytics/analytics.py
[... more checks ...]

============================================================
Validation Summary
============================================================
Project Structure......................✓ PASS
Python Environment......................✓ PASS
AWS Setup...............................✓ PASS
Terraform Setup.........................✓ PASS
Contact Information.....................✓ PASS
Tests...................................✓ PASS

Result: 6/6 checks passed
✓ All validations passed! Ready to deploy.
```

**If something fails:**
- Read the error message
- Follow the fix instruction shown
- Run `python validate.py` again

---

## 🧪 STEP 3: Test Part 1 - BLS Sync (3 minutes)

```powershell
python part_1_s3_sync/sync_bls_data.py
```

**Expected Output:**
```
2026-05-05 10:30:45,123 - INFO - Starting BLS data sync...
2026-05-05 10:30:45,456 - INFO - Fetching file list from BLS server
2026-05-05 10:30:47,789 - INFO - Found 45 files on BLS server
2026-05-05 10:30:48,012 - INFO - S3 bucket rearc-quest-data-123456789 exists
2026-05-05 10:30:49,345 - INFO - Successfully uploaded pr.data.0.Current to S3
2026-05-05 10:30:50,678 - INFO - Sync complete. Uploaded 8 new/updated files
```

**What happened:**
- ✅ Connected to AWS S3
- ✅ Created S3 bucket
- ✅ Downloaded files from BLS server
- ✅ Uploaded to S3

**Verify in AWS:**
```powershell
aws s3 ls | findstr rearc-quest
# Should show: rearc-quest-data-123456789

aws s3 ls s3://rearc-quest-data-123456789/bls_time_series/ | head -5
# Should show uploaded files
```

---

## 🌐 STEP 4: Test Part 2 - Population API (2 minutes)

```powershell
python part_2_api/fetch_population_data.py
```

**Expected Output:**
```
2026-05-05 10:31:45,123 - INFO - Fetching data from API
2026-05-05 10:31:46,456 - INFO - Successfully fetched data. Records: 8
2026-05-05 10:31:47,789 - INFO - Successfully saved data to s3://rearc-quest-data-123456789/population_data/population_data.json
```

**What happened:**
- ✅ Called DataUSA API
- ✅ Got population data for 8 years
- ✅ Saved as JSON to S3

**Verify in AWS:**
```powershell
# Download and view the data
aws s3 cp s3://rearc-quest-data-123456789/population_data/population_data.json - | head -20
```

**You should see JSON data with years 2013-2020**

---

## 📊 STEP 5: Test Part 3 - Analytics (5 minutes)

### 5.1 Create Test Data Directory

```powershell
mkdir data -Force
mkdir reports -Force
```

### 5.2 Download BLS Sample File

```powershell
# Note: This is faster than downloading from BLS every time
$url = "https://download.bls.gov/pub/time.series/pr/pr.data.0.Current"
$output = "data/pr.data.0.Current"
$headers = @{"User-Agent" = "your.email@example.com"}

Write-Host "Downloading BLS file... (this may take 1-2 minutes)"
Invoke-WebRequest -Uri $url -OutFile $output -Headers $headers

Write-Host "File downloaded to data/pr.data.0.Current"
```

### 5.3 Create Population Test Data

```powershell
$populationJson = @{
    data = @(
        @{Year = 2013; Population = 315005716},
        @{Year = 2014; Population = 317297725},
        @{Year = 2015; Population = 319297384},
        @{Year = 2016; Population = 322999999},
        @{Year = 2017; Population = 325084756},
        @{Year = 2018; Population = 327167439}
    )
} | ConvertTo-Json -Depth 10

$populationJson | Out-File -FilePath "data/population_data.json" -Encoding utf8

Write-Host "Population data created in data/population_data.json"
```

### 5.4 Run Analytics

```powershell
python part_3_analytics/analytics.py data/pr.data.0.Current data/population_data.json reports/
```

**Expected Output:**
```
2026-05-05 10:32:45,123 - INFO - Loading BLS data from data/pr.data.0.Current
2026-05-05 10:32:45,456 - INFO - Loaded BLS data with shape: (12345, 5)
2026-05-05 10:32:45,789 - INFO - Loading population data from data/population_data.json
2026-05-05 10:32:45,912 - INFO - Loaded population data with shape: (6, 2)
2026-05-05 10:32:46,123 - INFO - Generating Report 1: Population Statistics (2013-2018)
2026-05-05 10:32:46,234 - INFO - Report 1 Results: Mean=320923053.17, StdDev=5071423.51
2026-05-05 10:32:46,345 - INFO - Generating Report 2: Best Year per Series ID
2026-05-05 10:32:47,456 - INFO - Report 2 complete: 89 series found
2026-05-05 10:32:47,789 - INFO - Generating Report 3: Combined Analysis
2026-05-05 10:32:48,012 - INFO - Report 3 complete: 6 records found
2026-05-05 10:32:48,123 - INFO - All reports generated successfully
```

### 5.5 View Report Results

```powershell
# View Report 2 (Best year per series)
Write-Host "Report 2 Results:"
type reports/report_2_best_year.csv | Select-Object -First 5

# View Report 3 (Combined analysis)
Write-Host "`nReport 3 Results:"
type reports/report_3_combined.csv
```

**Report 2 sample:**
```
series_id,year,value
PRS30006011,1996,7
PRS30006012,2000,8
PRS30006021,1996,5
```

**Report 3 sample:**
```
series_id,year,period,value,Population
PRS30006032,2013,Q01,1.9,315005716
PRS30006032,2014,Q01,2.0,317297725
```

---

## 🧬 STEP 6: Run Unit Tests (2 minutes)

```powershell
# Install test dependencies
pip install pytest pytest-cov moto

# Run all tests
pytest tests/ -v
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

✅ **All tests passed!**

---

## 📦 STEP 7: Build Lambda Packages (2 minutes)

```powershell
.\build.ps1
```

**Expected Output:**
```
Building Lambda deployment packages...
Collecting boto3
Collecting requests
Collecting pandas
[... package installation ...]
Build complete!
Generated packages:
  - combined_lambda.zip
  - analytics_lambda.zip
  - python_dependencies.zip
```

**Verify files created:**
```powershell
ls *.zip
# Should show three .zip files
```

---

## 🚀 STEP 8: Deploy to AWS (10 minutes)

### 8.1 Option A: Fully Automated (Recommended)

```powershell
bash deploy.sh
```

**You'll be asked:**
```
Do you want to apply these changes? (yes/no):
```

**Type:** `yes` and press Enter

**Wait for:** "Deployment complete!"

### 8.2 Option B: Manual Terraform

If the script doesn't work:

```powershell
cd part_4_terraform

# Initialize terraform
terraform init

# Show plan
terraform plan

# Apply
terraform apply
# Type 'yes' when prompted
```

### 8.3 Save Deployment Info

```powershell
cd part_4_terraform
terraform output > ..\deployment_info.txt
cd ..

# View your deployment
type deployment_info.txt
```

**Save this file! It contains:**
- S3 bucket name
- Lambda function names
- SQS queue URL
- Log group names

---

## ✅ STEP 9: Verify Deployment (5 minutes)

### 9.1 Check S3 Bucket

```powershell
aws s3 ls | findstr rearc-quest
# Should show: rearc-quest-data-123456789
```

### 9.2 Check Lambda Functions

```powershell
aws lambda list-functions | findstr rearc-quest
# Should show:
# - rearc-quest-combined-data-pipeline
# - rearc-quest-analytics
```

### 9.3 Check SQS Queue

```powershell
aws sqs list-queues | findstr rearc-quest
# Should show: rearc-quest-analytics-queue
```

### 9.4 Check EventBridge Rule

```powershell
aws events describe-rule --name rearc-quest-daily-schedule
# Should show: ENABLED
```

---

## 🧪 STEP 10: Test Lambda Functions (5 minutes)

### 10.1 Invoke Combined Lambda

```powershell
aws lambda invoke `
  --function-name rearc-quest-combined-data-pipeline `
  response.json

# View response
type response.json
```

**Expected Response:**
```json
{
  "statusCode": 200,
  "body": "{\"timestamp\": \"2026-05-05T10:35:00\", \"part_1_bls_sync\": {\"success\": true}, \"part_2_population_api\": {\"success\": true}}"
}
```

### 10.2 Check Lambda Logs

```powershell
# View logs from last 5 minutes
aws logs tail /aws/lambda/rearc-quest-combined-data-pipeline --since 5m

# Follow logs in real-time (Press Ctrl+C to stop)
aws logs tail /aws/lambda/rearc-quest-combined-data-pipeline --follow
```

**You should see:**
```
2026-05-05 10:35:45 - Starting combined data pipeline...
2026-05-05 10:35:46 - Starting Part 1: BLS data sync
2026-05-05 10:35:48 - BLS sync complete
2026-05-05 10:35:49 - Starting Part 2: Population data fetch
2026-05-05 10:35:51 - Population data saved to S3
```

### 10.3 Check Analytics Lambda

```powershell
# View analytics logs
aws logs tail /aws/lambda/rearc-quest-analytics --since 10m
```

---

## 🎉 STEP 11: You're Done! 

### Checklist:
- ✅ Environment validated
- ✅ Part 1 tested locally
- ✅ Part 2 tested locally
- ✅ Part 3 tested locally
- ✅ Unit tests passed
- ✅ Lambda packages built
- ✅ AWS infrastructure deployed
- ✅ Lambdas invoked and working
- ✅ Logs verified

### What's Happening Now:
- 🕐 Every day at 2 AM UTC
- 📥 Combined Lambda runs Part 1 & 2
- 📤 Files sync to S3
- 📨 SQS receives notification
- 📊 Analytics Lambda runs Part 3
- 📋 Reports logged to CloudWatch

### Next Steps:
1. **Monitor Tomorrow:** Check logs at 2 AM UTC
2. **Submit:** Follow `SUBMISSION_CHECKLIST.md`
3. **Interview:** Be ready to explain:
   - How each part works
   - Why you chose this architecture
   - How to scale it
   - Cost considerations

---

## 🆘 Quick Troubleshooting

### "Command not found: bash"
→ You're on Windows. Make sure Git Bash is installed or use PowerShell scripts.

### "AWS credentials not configured"
→ Run `aws configure` first

### "BLS 403 Forbidden"
→ Update email in Python files

### "Lambda function not found"
→ Wait 1-2 minutes after deploy and try again

### "Terraform not initialized"
→ Run `cd part_4_terraform && terraform init`

### "Permission denied"
→ Check IAM role has S3 and CloudWatch permissions

---

## 📞 Need Help?

- **Detailed commands:** See `COMMANDS_QUICK_REFERENCE.md`
- **Full documentation:** See `TESTING_GUIDE.md`
- **Setup issues:** See `QUICK_START.md`
- **Submission help:** See `SUBMISSION_CHECKLIST.md`

---

**Congratulations! Your Rearc Data Quest implementation is complete and deployed! 🎉**
