Param(
    [switch]$Force
)

Write-Host "==============================================="
Write-Host "Rearc Data Quest - Terraform Destroy"
Write-Host "==============================================="

if (-not (Get-Command terraform -ErrorAction SilentlyContinue)) {
    Write-Error "Error: Terraform is not installed"
    exit 1
}

Set-Location -Path ".\part_4_terraform"

Write-Host "Initializing Terraform..."
terraform init -input=false

if ($Force) {
    terraform destroy -auto-approve
} else {
    terraform destroy
}

Remove-Item -Force -ErrorAction SilentlyContinue .\terraform.tfstate, .\terraform.tfstate.backup

Write-Host "Destroy complete. All Terraform-managed AWS resources should be removed."
