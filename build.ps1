# PowerShell build script for Lambda packages (Windows)

Write-Host "Building Lambda deployment packages..."

# Clean up old packages
Remove-Item -Force "combined_lambda.zip" -ErrorAction SilentlyContinue
Remove-Item -Force "analytics_lambda.zip" -ErrorAction SilentlyContinue
Remove-Item -Force "python_dependencies.zip" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "build" -ErrorAction SilentlyContinue

# Create temp directories
New-Item -ItemType Directory -Force -Path "build\lambda" | Out-Null
New-Item -ItemType Directory -Force -Path "build\deps" | Out-Null

# Copy Lambda functions
Copy-Item "lambda_functions\combined_lambda.py" "build\lambda\"
Copy-Item "lambda_functions\analytics_lambda.py" "build\lambda\"
Copy-Item "part_1_s3_sync\sync_bls_data.py" "build\lambda\"
Copy-Item "part_2_api\fetch_population_data.py" "build\lambda\"
Copy-Item "part_3_analytics\analytics.py" "build\lambda\"

# Create __init__.py files
New-Item -Path "build\lambda\__init__.py" -ItemType File | Out-Null
New-Item -Path "build\lambda\part_1_s3_sync\__init__.py" -ItemType File -ErrorAction SilentlyContinue | Out-Null
New-Item -Path "build\lambda\part_2_api\__init__.py" -ItemType File -ErrorAction SilentlyContinue | Out-Null
New-Item -Path "build\lambda\part_3_analytics\__init__.py" -ItemType File -ErrorAction SilentlyContinue | Out-Null

# Install dependencies
pip install --target "build\deps" -r requirements.txt

# Create Lambda packages
# Using Compress-Archive (built-in PowerShell)
Compress-Archive -Path "build\lambda\*" -DestinationPath "combined_lambda.zip" -Force
Compress-Archive -Path "build\lambda\*" -DestinationPath "analytics_lambda.zip" -Force
Compress-Archive -Path "build\deps\*" -DestinationPath "python_dependencies.zip" -Force

# Clean up
Remove-Item -Recurse -Force "build"

Write-Host "Build complete!" -ForegroundColor Green
Write-Host "Generated packages:"
Write-Host "  - combined_lambda.zip"
Write-Host "  - analytics_lambda.zip"
Write-Host "  - python_dependencies.zip"
