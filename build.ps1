Write-Host "Building Lambda deployment packages..."

Remove-Item -Force "combined_lambda.zip","analytics_lambda.zip","python_dependencies.zip" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "build" -ErrorAction SilentlyContinue

$packageRoot = "build\package"
$depsRoot = "build\deps"

New-Item -ItemType Directory -Force -Path "$packageRoot\lambda_functions" | Out-Null
New-Item -ItemType Directory -Force -Path "$packageRoot\part_1_s3_sync" | Out-Null
New-Item -ItemType Directory -Force -Path "$packageRoot\part_2_api" | Out-Null
New-Item -ItemType Directory -Force -Path "$packageRoot\part_3_analytics" | Out-Null
New-Item -ItemType Directory -Force -Path $depsRoot | Out-Null

Copy-Item "lambda_functions\combined_lambda.py" "$packageRoot\lambda_functions\"
Copy-Item "lambda_functions\analytics_lambda.py" "$packageRoot\lambda_functions\"
Copy-Item "part_1_s3_sync\sync_bls_data.py" "$packageRoot\part_1_s3_sync\"
Copy-Item "part_2_api\fetch_population_data.py" "$packageRoot\part_2_api\"
Copy-Item "part_3_analytics\analytics.py" "$packageRoot\part_3_analytics\"

New-Item -Path "$packageRoot\lambda_functions\__init__.py" -ItemType File -Force | Out-Null
New-Item -Path "$packageRoot\part_1_s3_sync\__init__.py" -ItemType File -Force | Out-Null
New-Item -Path "$packageRoot\part_2_api\__init__.py" -ItemType File -Force | Out-Null
New-Item -Path "$packageRoot\part_3_analytics\__init__.py" -ItemType File -Force | Out-Null

pip install --target $depsRoot -r requirements.txt

Compress-Archive -Path "$packageRoot\*" -DestinationPath "combined_lambda.zip" -Force
Copy-Item -Path "combined_lambda.zip" -Destination "analytics_lambda.zip" -Force
Compress-Archive -Path "$depsRoot\*" -DestinationPath "python_dependencies.zip" -Force

Remove-Item -Recurse -Force "build"

Write-Host "Build complete!" -ForegroundColor Green
Write-Host "Generated packages:`n  - combined_lambda.zip`n  - analytics_lambda.zip`n  - python_dependencies.zip"