"""
Validation script to check if everything is set up correctly
Run this before deployment to verify your setup
"""

import sys
import subprocess
import os
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"{text}")
    print(f"{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def check_file(path, description):
    """Check if a file exists"""
    if Path(path).exists():
        print_success(f"{description}: {path}")
        return True
    else:
        print_error(f"Missing {description}: {path}")
        return False

def check_python_import(module_name):
    """Check if a Python module can be imported"""
    try:
        __import__(module_name)
        print_success(f"Python module available: {module_name}")
        return True
    except ImportError:
        print_error(f"Python module not found: {module_name}")
        return False

def check_command(command, description):
    """Check if a command is available"""
    try:
        result = subprocess.run(f"{command} --version", shell=True, 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print_success(f"{description} is installed")
            return True
    except:
        pass
    print_error(f"{description} is not installed or not in PATH")
    return False

def validate_project_structure():
    """Validate project directory structure"""
    print_header("Validating Project Structure")
    
    files_to_check = [
        ("part_1_s3_sync/sync_bls_data.py", "Part 1: BLS Sync"),
        ("part_2_api/fetch_population_data.py", "Part 2: Population API"),
        ("part_3_analytics/analytics.py", "Part 3: Analytics"),
        ("part_4_terraform/main.tf", "Part 4: Terraform Main"),
        ("part_4_terraform/variables.tf", "Part 4: Variables"),
        ("part_4_terraform/outputs.tf", "Part 4: Outputs"),
        ("lambda_functions/combined_lambda.py", "Lambda: Combined"),
        ("lambda_functions/analytics_lambda.py", "Lambda: Analytics"),
        ("requirements.txt", "Python Requirements"),
        ("setup.py", "Package Setup"),
        ("README.md", "README"),
        ("QUICK_START.md", "Quick Start Guide"),
        ("IMPLEMENTATION_GUIDE.md", "Implementation Guide"),
        ("SUBMISSION_CHECKLIST.md", "Submission Checklist"),
        ("PROJECT_SUMMARY.md", "Project Summary"),
    ]
    
    all_ok = True
    for filepath, description in files_to_check:
        if not check_file(filepath, description):
            all_ok = False
    
    return all_ok

def validate_python_environment():
    """Validate Python environment and dependencies"""
    print_header("Validating Python Environment")
    
    # Check Python version
    version_info = sys.version_info
    if version_info.major >= 3 and version_info.minor >= 11:
        print_success(f"Python {version_info.major}.{version_info.minor} (Required: 3.11+)")
    else:
        print_error(f"Python {version_info.major}.{version_info.minor} (Required: 3.11+)")
        return False
    
    # Check required packages
    modules_to_check = [
        ('boto3', 'AWS SDK'),
        ('requests', 'HTTP Client'),
        ('pandas', 'Data Processing'),
    ]
    
    all_ok = True
    for module, description in modules_to_check:
        if not check_python_import(module):
            all_ok = False
    
    return all_ok

def validate_aws_setup():
    """Validate AWS configuration"""
    print_header("Validating AWS Setup")
    
    all_ok = True
    
    # Check AWS CLI
    if not check_command("aws", "AWS CLI"):
        all_ok = False
    
    # Check AWS credentials
    try:
        result = subprocess.run("aws sts get-caller-identity", shell=True,
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print_success("AWS credentials configured")
        else:
            print_error("AWS credentials not configured")
            print_warning("Run: aws configure")
            all_ok = False
    except Exception as e:
        print_error(f"AWS credentials check failed: {e}")
        all_ok = False
    
    return all_ok

def validate_terraform_setup():
    """Validate Terraform setup"""
    print_header("Validating Terraform Setup")
    
    all_ok = check_command("terraform", "Terraform")
    
    # Check Terraform files
    if Path("part_4_terraform").exists():
        terraform_files = list(Path("part_4_terraform").glob("*.tf"))
        if terraform_files:
            print_success(f"Found {len(terraform_files)} Terraform files")
        else:
            print_error("No Terraform files found in part_4_terraform/")
            all_ok = False
    else:
        print_error("part_4_terraform/ directory not found")
        all_ok = False
    
    return all_ok

def validate_contact_info():
    """Check if contact information is configured"""
    print_header("Validating Contact Information (BLS Compliance)")
    
    files_to_check = [
        "part_1_s3_sync/sync_bls_data.py",
        "part_2_api/fetch_population_data.py"
    ]
    
    all_ok = True
    for filepath in files_to_check:
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                if "your.email@example.com" in content or "contact@yourcompany.com" in content:
                    print_warning(f"Update email in: {filepath}")
                    all_ok = False
                else:
                    print_success(f"Email configured in: {filepath}")
        except Exception as e:
            print_error(f"Could not read {filepath}: {e}")
            all_ok = False
    
    return all_ok

def validate_tests():
    """Check if tests exist and can run"""
    print_header("Validating Tests")
    
    test_files = list(Path("tests").glob("test_*.py"))
    if test_files:
        print_success(f"Found {len(test_files)} test files")
        return True
    else:
        print_warning("No test files found")
        return False

def run_validation():
    """Run all validations"""
    print(f"\n{Colors.BLUE}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║         Rearc Data Quest - Setup Validation                ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}")
    
    results = {
        "Project Structure": validate_project_structure(),
        "Python Environment": validate_python_environment(),
        "AWS Setup": validate_aws_setup(),
        "Terraform Setup": validate_terraform_setup(),
        "Contact Information": validate_contact_info(),
        "Tests": validate_tests(),
    }
    
    print_header("Validation Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for check, result in results.items():
        status = f"{Colors.GREEN}✓ PASS{Colors.END}" if result else f"{Colors.RED}✗ FAIL{Colors.END}"
        print(f"{check:.<40} {status}")
    
    print(f"\n{Colors.BLUE}Result: {passed}/{total} checks passed{Colors.END}\n")
    
    if passed == total:
        print_success("All validations passed! Ready to deploy.")
        return 0
    else:
        failed = total - passed
        print_error(f"{failed} validation(s) failed. Please fix issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(run_validation())
