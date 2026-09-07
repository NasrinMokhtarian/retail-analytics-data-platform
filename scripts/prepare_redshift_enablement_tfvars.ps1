param(
    [string]$TerraformDevDir = "infra\terraform\environments\dev",
    [int]$BaseCapacity = 4,
    [int]$MaxCapacity = 4,
    [int]$UsageLimitAmount = 1
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path "$PSScriptRoot\.."
$TerraformDir = Join-Path $ProjectRoot $TerraformDevDir
$OutputPath = Join-Path $TerraformDir "redshift_enablement.local.tfvars"

if (-not (Test-Path $TerraformDir)) {
    throw "Terraform dev directory does not exist: $TerraformDir"
}

Write-Host "Detecting current public IP..."

$PublicIp = (Invoke-RestMethod -Uri "https://checkip.amazonaws.com").Trim()

if ([string]::IsNullOrWhiteSpace($PublicIp)) {
    throw "Could not detect public IP."
}

$AllowedCidr = "$PublicIp/32"

$Lines = @(
    "# Local-only Redshift enablement values.",
    "# Do not commit this file.",
    "# Created for one short Redshift test window.",
    "",
    "enable_redshift = true",
    "",
    "redshift_base_capacity       = $BaseCapacity",
    "redshift_max_capacity        = $MaxCapacity",
    "redshift_usage_limit_amount  = $UsageLimitAmount",
    "redshift_publicly_accessible = true",
    "redshift_allowed_cidr_blocks = [`"$AllowedCidr`"]",
    "redshift_subnet_ids          = []"
)

$Lines | Set-Content -Path $OutputPath -Encoding UTF8

Write-Host ""
Write-Host "Created local Redshift enablement file:"
Write-Host $OutputPath
Write-Host ""
Write-Host "Allowed CIDR:"
Write-Host $AllowedCidr
Write-Host ""
Write-Host "IMPORTANT:"
Write-Host "This file enables Redshift only when you explicitly pass it with -var-file."
Write-Host "Do not commit this file."
Write-Host "Do not run terraform apply yet."