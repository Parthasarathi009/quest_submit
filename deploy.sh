# Deployment script for Terraform infrastructure

#!/bin/bash
set -e

echo "==============================================="
echo "Rearc Data Quest - Infrastructure Deployment"
echo "==============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command -v terraform &> /dev/null; then
    echo -e "${RED}Error: Terraform is not installed${NC}"
    exit 1
fi

if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: AWS CLI is not installed${NC}"
    exit 1
fi

if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}Error: AWS credentials are not configured${NC}"
    exit 1
fi

echo -e "${GREEN}Prerequisites OK${NC}"
echo ""

# Navigate to Terraform directory
cd part_4_terraform

# Initialize Terraform
echo -e "${YELLOW}Initializing Terraform...${NC}"
terraform init

# Validate configuration
echo -e "${YELLOW}Validating Terraform configuration...${NC}"
terraform validate

# Show plan
echo -e "${YELLOW}Generating Terraform plan...${NC}"
terraform plan -out=tfplan

# Ask for confirmation
echo ""
echo -e "${YELLOW}Please review the plan above.${NC}"
read -p "Do you want to apply these changes? (yes/no): " confirmation

if [ "$confirmation" != "yes" ]; then
    echo "Deployment cancelled"
    rm -f tfplan
    exit 0
fi

# Apply configuration
echo -e "${YELLOW}Applying Terraform configuration...${NC}"
terraform apply tfplan

# Clean up
rm -f tfplan

# Show outputs
echo ""
echo -e "${GREEN}Deployment complete!${NC}"
echo ""
echo "Outputs:"
terraform output

echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Verify resources in AWS Console"
echo "2. Manually trigger the combined Lambda to test"
echo "3. Check CloudWatch logs for any errors"
