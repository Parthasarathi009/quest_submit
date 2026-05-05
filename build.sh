# Build and deployment helper script for AWS Lambda packages

#!/bin/bash
set -e

echo "Building Lambda deployment packages..."

# Clean up old packages
rm -f combined_lambda.zip analytics_lambda.zip python_dependencies.zip

# Create temp directories
mkdir -p build/lambda build/deps

# Copy Lambda functions
cp lambda_functions/combined_lambda.py build/lambda/
cp lambda_functions/analytics_lambda.py build/lambda/
cp part_1_s3_sync/sync_bls_data.py build/lambda/
cp part_2_api/fetch_population_data.py build/lambda/
cp part_3_analytics/analytics.py build/lambda/

# Create __init__.py files
touch build/lambda/__init__.py
touch build/lambda/part_1_s3_sync/__init__.py
touch build/lambda/part_2_api/__init__.py
touch build/lambda/part_3_analytics/__init__.py

# Install dependencies
pip install --target build/deps -r requirements.txt

# Create combined Lambda package
cd build/lambda
zip -r ../../combined_lambda.zip .
zip -r ../../analytics_lambda.zip . -x "*.pyc"
cd ../..

# Create dependencies layer
cd build/deps
zip -r ../../python_dependencies.zip .
cd ../..

# Clean up
rm -rf build/

echo "Build complete!"
echo "Generated packages:"
echo "  - combined_lambda.zip"
echo "  - analytics_lambda.zip"
echo "  - python_dependencies.zip"
