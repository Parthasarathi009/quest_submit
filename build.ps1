# Guard: make sure venv is active so we use the right python
if (-not $env:VIRTUAL_ENV) {
    Write-Error "No active virtualenv detected. Run: .\venv\Scripts\Activate.ps1 first."
    exit 1
}
Write-Host "Using venv: $env:VIRTUAL_ENV" -ForegroundColor Cyan
Write-Host "Building Lambda deployment packages..."

Remove-Item -Force "combined_lambda.zip","analytics_lambda.zip","python_dependencies.zip" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "build" -ErrorAction SilentlyContinue

$packageRoot = "build\package"
$depsRoot    = "build\deps"

New-Item -ItemType Directory -Force -Path "$packageRoot\lambda_functions" | Out-Null
New-Item -ItemType Directory -Force -Path "$packageRoot\part_1_s3_sync"   | Out-Null
New-Item -ItemType Directory -Force -Path "$packageRoot\part_2_api"       | Out-Null
New-Item -ItemType Directory -Force -Path "$packageRoot\part_3_analytics" | Out-Null
New-Item -ItemType Directory -Force -Path $depsRoot                       | Out-Null

Copy-Item "lambda_functions\combined_lambda.py"        "$packageRoot\lambda_functions\"
Copy-Item "lambda_functions\analytics_lambda.py"       "$packageRoot\lambda_functions\"
Copy-Item "part_1_s3_sync\sync_bls_data.py"            "$packageRoot\part_1_s3_sync\"
Copy-Item "part_2_api\fetch_population_data.py"        "$packageRoot\part_2_api\"
Copy-Item "part_3_analytics\analytics.py"              "$packageRoot\part_3_analytics\"

New-Item -Path "$packageRoot\lambda_functions\__init__.py" -ItemType File -Force | Out-Null
New-Item -Path "$packageRoot\part_1_s3_sync\__init__.py"   -ItemType File -Force | Out-Null
New-Item -Path "$packageRoot\part_2_api\__init__.py"       -ItemType File -Force | Out-Null
New-Item -Path "$packageRoot\part_3_analytics\__init__.py" -ItemType File -Force | Out-Null

# Install dependencies into the layer folder
# pip install --target $depsRoot -r requirements.txt
# Use python -m pip to ensure we use the active venv's pip,
# and --ignore-installed so venv packages don't interfere
python -m pip install --target $depsRoot --ignore-installed -r requirements.txt

# ---------------------------------------------------------------
# FIX: Strip packages that are already built into the Lambda
# Python 3.11 runtime, so we don't bloat the layer zip.
#
# boto3      ~3MB  \
# botocore   ~40MB  > all pre-installed in the Lambda runtime
# s3transfer ~1MB  /
# urllib3 and six are pulled in by botocore — remove them too
# unless your own code imports them directly.
#
# BEFORE this fix: python_dependencies.zip was ~67MB+ → 413 error
# AFTER  this fix: typically drops to ~10-20MB → well under limit
# ---------------------------------------------------------------
$packagesToRemove = @(
    "boto3",
    "botocore",
    "s3transfer",
    "boto3-*.dist-info",
    "botocore-*.dist-info",
    "s3transfer-*.dist-info"
)

foreach ($pkg in $packagesToRemove) {
    $path = Join-Path $depsRoot $pkg
    if (Test-Path $path) {
        Remove-Item -Recurse -Force $path
        Write-Host "  Removed $pkg from layer (already in Lambda runtime)" -ForegroundColor Yellow
    }
}

# Also remove all .dist-info and __pycache__ folders — not needed at runtime
Get-ChildItem -Path $depsRoot -Recurse -Directory |
    Where-Object { $_.Name -like "*.dist-info" -or $_.Name -eq "__pycache__" } |
    Remove-Item -Recurse -Force

# Show final layer size so you can verify it's under 67MB
$layerSizeMB = [math]::Round((Get-ChildItem -Recurse $depsRoot | Measure-Object -Property Length -Sum).Sum / 1MB, 2)
Write-Host "  Layer folder size before zipping: $layerSizeMB MB" -ForegroundColor Cyan
if ($layerSizeMB -gt 60) {
    Write-Warning "Layer is still $layerSizeMB MB — close to or over the 67MB direct-upload limit."
    Write-Warning "The Terraform config uploads via S3 to handle this, but consider trimming requirements.txt."
}

Compress-Archive -Path "$packageRoot\*" -DestinationPath "combined_lambda.zip"  -Force
Copy-Item         -Path "combined_lambda.zip" -Destination "analytics_lambda.zip" -Force
Compress-Archive -Path "$depsRoot\*"     -DestinationPath "python_dependencies.zip" -Force

Remove-Item -Recurse -Force "build"

Write-Host "Build complete!" -ForegroundColor Green
Write-Host "Generated packages:"
Write-Host "  - combined_lambda.zip"
Write-Host "  - analytics_lambda.zip"
Write-Host "  - python_dependencies.zip"
