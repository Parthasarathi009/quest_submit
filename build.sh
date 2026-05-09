#!/bin/bash
set -e

echo "Building Lambda deployment packages..."

rm -f combined_lambda.zip analytics_lambda.zip python_dependencies.zip
rm -rf build/

mkdir -p build/package/lambda_functions
mkdir -p build/package/part_1_s3_sync
mkdir -p build/package/part_2_api
mkdir -p build/package/part_3_analytics
mkdir -p build/deps

cp lambda_functions/combined_lambda.py build/package/lambda_functions/
cp lambda_functions/analytics_lambda.py build/package/lambda_functions/
cp part_1_s3_sync/sync_bls_data.py build/package/part_1_s3_sync/
cp part_2_api/fetch_population_data.py build/package/part_2_api/
cp part_3_analytics/analytics.py build/package/part_3_analytics/

touch build/package/lambda_functions/__init__.py
touch build/package/part_1_s3_sync/__init__.py
touch build/package/part_2_api/__init__.py
touch build/package/part_3_analytics/__init__.py

pip install --target build/deps -r requirements.txt

cd build/package
zip -r ../../combined_lambda.zip .
cp ../../combined_lambda.zip ../../analytics_lambda.zip
cd ../..

cd build/deps
zip -r ../../python_dependencies.zip .
cd ../..

rm -rf build/

echo "Build complete!"
echo "Generated packages:"
echo "  - combined_lambda.zip"
echo "  - analytics_lambda.zip"
echo "  - python_dependencies.zip"