if (-not $env:VIRTUAL_ENV) {
    Write-Error "No active virtualenv detected. Run: .\venv\Scripts\Activate.ps1 first."
    exit 1
}
Write-Host "Using venv: $env:VIRTUAL_ENV" -ForegroundColor Cyan

Write-Host "Building Lambda deployment packages..."

Remove-Item -Force "combined_lambda.zip","analytics_lambda.zip","python_dependencies.zip" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "build" -ErrorAction SilentlyContinue

$packageRoot = "build\package"

New-Item -ItemType Directory -Force -Path "$packageRoot\lambda_functions" | Out-Null
New-Item -ItemType Directory -Force -Path "$packageRoot\part_1_s3_sync"   | Out-Null
New-Item -ItemType Directory -Force -Path "$packageRoot\part_2_api"       | Out-Null
New-Item -ItemType Directory -Force -Path "$packageRoot\part_3_analytics" | Out-Null

Copy-Item "lambda_functions\combined_lambda.py"        "$packageRoot\lambda_functions\"
Copy-Item "lambda_functions\analytics_lambda.py"       "$packageRoot\lambda_functions\"
Copy-Item "part_1_s3_sync\sync_bls_data.py"            "$packageRoot\part_1_s3_sync\"
Copy-Item "part_2_api\fetch_population_data.py"        "$packageRoot\part_2_api\"
Copy-Item "part_3_analytics\analytics.py"              "$packageRoot\part_3_analytics\"

New-Item -Path "$packageRoot\lambda_functions\__init__.py" -ItemType File -Force | Out-Null
New-Item -Path "$packageRoot\part_1_s3_sync\__init__.py"   -ItemType File -Force | Out-Null
New-Item -Path "$packageRoot\part_2_api\__init__.py"       -ItemType File -Force | Out-Null
New-Item -Path "$packageRoot\part_3_analytics\__init__.py" -ItemType File -Force | Out-Null

# Bundle small dependencies (requests, python-dotenv) directly into the
# Lambda zip. pandas + numpy are provided by the AWS managed layer
# AWSSDKPandas-Python311 declared in main.tf - no custom layer needed.
# boto3 is pre-installed in the Lambda runtime - do not bundle it.
Write-Host "Installing small dependencies into package..."
python -m pip install --target $packageRoot --ignore-installed requests python-dotenv -q

# Remove .dist-info and __pycache__ - not needed at runtime
Get-ChildItem -Path $packageRoot -Recurse -Directory |
    Where-Object { $_.Name -like "*.dist-info" -or $_.Name -eq "__pycache__" } |
    Remove-Item -Recurse -Force

$zipSizeMB = [math]::Round(
    (Get-ChildItem -Recurse $packageRoot | Measure-Object -Property Length -Sum).Sum / 1MB,
    2
)
Write-Host "  Package folder size: $zipSizeMB MB" -ForegroundColor Cyan

Compress-Archive -Path "$packageRoot\*" -DestinationPath "combined_lambda.zip" -Force
Copy-Item -Path "combined_lambda.zip" -Destination "analytics_lambda.zip"      -Force

Remove-Item -Recurse -Force "build"

Write-Host "Build complete!" -ForegroundColor Green
Write-Host "Generated packages:"
Write-Host "  - combined_lambda.zip"
Write-Host "  - analytics_lambda.zip"
Write-Host ""
Write-Host "Note: pandas + numpy are provided by the AWS managed layer" -ForegroundColor Yellow
Write-Host "      AWSSDKPandas-Python311 - no python_dependencies.zip needed." -ForegroundColor Yellow
