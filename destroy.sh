#!/bin/bash
set -e

echo "==============================================="
echo "Rearc Data Quest - Terraform Destroy"
echo "==============================================="

echo "Checking prerequisites..."
if ! command -v terraform >/dev/null 2>&1; then
  echo "Error: Terraform is not installed"
  exit 1
fi

cd part_4_terraform

echo "Initializing Terraform..."
terraform init -input=false

echo "Destroying Terraform-managed resources..."
terraform destroy -auto-approve

rm -f terraform.tfstate terraform.tfstate.backup

echo "Destroy complete. All Terraform-managed AWS resources should be removed."
