# Quick Command Reference - Testing & Deployment

## 🎯 Most Common Commands

### Validate Everything (Start Here!)
```powershell
python validate.py
```

### Test Individual Parts (Local)
```powershell
# Part 1: BLS Sync
python part_1_s3_sync/sync_bls_data.py

# Part 2: Population API
python part_2_api/fetch_population_data.py

# Part 3: Analytics
python part_3_analytics/analytics.py data/pr.data.0.Current data/population_data.json reports/
```

### Run Tests
```powershell
# All tests
pytest tests/ -v

# Specific part
pytest tests/test_part1.py -v
pytest tests/test_part2.py -v
pytest tests/test_part3.py -v
```

### Deploy to AWS
```powershell
# Automated (recommended)
bash deploy.sh

# Manual
cd part_4_terraform
terraform apply
cd ..
```

### Test Lambda in AWS
```powershell
# Invoke combined lambda
aws lambda invoke --function-name rearc-quest-combined-data-pipeline response.json
type response.json

# View logs
aws logs tail /aws/lambda/rearc-quest-combined-data-pipeline --follow
```

### Check AWS Resources
```powershell
# List S3 buckets
aws s3 ls | findstr rearc-quest

# List Lambda functions
aws lambda list-functions | findstr rearc-quest

# View S3 data
aws s3 ls s3://rearc-quest-data-[ACCOUNT-ID]/ --recursive
```

---

## 📋 Testing Stages (In Order)

### Stage 1: Local Validation (5 min)
```
✓ python validate.py
```

### Stage 2: Individual Parts (10 min)
```
✓ python part_1_s3_sync/sync_bls_data.py
✓ python part_2_api/fetch_population_data.py
✓ python part_3_analytics/analytics.py data/pr.data.0.Current data/population_data.json reports/
```

### Stage 3: Unit Tests (2 min)
```
✓ pytest tests/ -v
```

### Stage 4: Build & Deploy (10 min)
```
✓ .\build.ps1
✓ bash deploy.sh
```

### Stage 5: Verify in AWS (5 min)
```
✓ aws lambda invoke --function-name rearc-quest-combined-data-pipeline response.json
✓ aws logs tail /aws/lambda/rearc-quest-combined-data-pipeline --since 5m
```

---

## 🔧 Configuration Files to Update

### Before First Run
```
1. part_1_s3_sync/sync_bls_data.py - Line 24
   Change: "contact@yourcompany.com" 
   To: "your.email@example.com"

2. part_2_api/fetch_population_data.py - Line 24
   Change: "contact@yourcompany.com"
   To: "your.email@example.com"
```

### Before AWS Deployment
```
1. part_4_terraform/terraform.tfvars
   Copy from: terraform.tfvars.example
   Update: your AWS region, environment name, etc.
```

---

## 📊 Expected Outputs

### Part 1 Success
```
✓ Starting BLS data sync...
✓ Found 45 files on BLS server
✓ Successfully uploaded pr.data.0.Current to S3
✓ Sync complete. Uploaded 10 new/updated files
```

### Part 2 Success
```
✓ Fetching data from API...
✓ Successfully fetched data. Records: 8
✓ Successfully saved data to s3://...population_data.json
```

### Part 3 Success
```
✓ Report 1: Mean=320923053.17, StdDev=5071423.51
✓ Report 2 complete: 89 series found
✓ Report 3 complete: 6 records found
✓ Saved report to reports/report_2_best_year.csv
✓ Saved report to reports/report_3_combined.csv
```

### Lambda Success
```
{
  "statusCode": 200,
  "body": {
    "part_1_bls_sync": { "success": true },
    "part_2_population_api": { "success": true }
  }
}
```

---

## ❌ Common Errors & Fixes

| Error | Fix |
|-------|-----|
| `403 Forbidden` | Update email in Python files |
| `ModuleNotFoundError` | `pip install -r requirements.txt` |
| `NoCredentialsError` | `aws configure` |
| `Function not found` | Run `bash deploy.sh` first |
| `Terraform not initialized` | `cd part_4_terraform && terraform init` |
| `Lambda timeout` | Increase `lambda_timeout` in variables |

---

## 🎯 One-Command Testing

Run complete test sequence:

```powershell
# Validate -> Test -> Deploy -> Verify (All in one script)
python validate.py; `
pytest tests/ -v; `
.\build.ps1; `
bash deploy.sh; `
aws lambda invoke --function-name rearc-quest-combined-data-pipeline response.json; `
type response.json
```

---

## 📖 Detailed Guides

- **Full Testing Guide:** `TESTING_GUIDE.md` (this document)
- **Quick Start:** `QUICK_START.md` (5-minute setup)
- **Implementation:** `IMPLEMENTATION_GUIDE.md` (comprehensive)
- **Submission:** `SUBMISSION_CHECKLIST.md` (pre-submission)

---

## 💡 Pro Tips

1. **Run validation first:** Always start with `python validate.py`
2. **Test locally before AWS:** Never deploy without local testing
3. **Check logs often:** `aws logs tail ... --follow` is your friend
4. **Use terraform plan:** Always review `terraform plan` before `terraform apply`
5. **Keep deployment info:** Save `terraform output` for reference
6. **Monitor costs:** Check AWS cost explorer regularly
7. **Clean up:** Run `terraform destroy` when done

---

## 📞 Need Help?

Check the relevant section in `TESTING_GUIDE.md`:
- Local testing issues → Troubleshooting Local Scripts
- AWS issues → Troubleshooting Lambda/AWS
- Deployment issues → Deploy to AWS section
- Any part → Search the IMPLEMENTATION_GUIDE.md
